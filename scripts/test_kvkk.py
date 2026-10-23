# -*- coding: utf-8 -*-
"""
test_kvkk.py
------------
KVKK Başvuru Portalı Kapsamlı Entegrasyon ve Birim Test Paketi:
1. SQLite veritabanı şeması ve dinamik kolon kontrolü
2. 30 günlük yasal süre sayacı (KVKK Md. 13/2) ve acil uyarı seviyeleri
3. KEP adresi formatı ve BTK KEPHS doğrulayıcısı
4. İlgili kişi durum sorgulama (/takip) ve veri maskeleme
5. Veri sorumlusu durum güncelleme ve gerekçeli karar notu
"""

import os
import sys
import json
import sqlite3
import datetime
import unittest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import init_db, DB_FILE
from scripts.kvkk_validation_engine import (
    validate_kep_address,
    calculate_deadline_metrics,
    mask_full_name,
    build_public_status_view
)

class TestKVKKPortal(unittest.TestCase):
    def setUp(self):
        init_db()
        with sqlite3.connect(DB_FILE) as conn:
            conn.cursor().execute("DELETE FROM submissions WHERE tracking_code LIKE 'KVKK-2026-TEST%'")
            conn.commit()

    def tearDown(self):
        with sqlite3.connect(DB_FILE) as conn:
            conn.cursor().execute("DELETE FROM submissions WHERE tracking_code LIKE 'KVKK-2026-TEST%'")
            conn.commit()

    def test_database_initialization(self):
        self.assertTrue(os.path.exists(DB_FILE), "SQLite veritabani dosyasi olusturulamadi.")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='submissions'")
            table = cursor.fetchone()
            self.assertIsNotNone(table, "'submissions' tablosu veritabaninda bulunamadi.")

            cursor.execute("PRAGMA table_info(submissions)")
            columns = [row[1] for row in cursor.fetchall()]
            self.assertIn("tracking_code", columns)
            self.assertIn("status", columns)
            self.assertIn("resolution_note", columns)
            self.assertIn("kep_address", columns)

    def test_application_submission_flow(self):
        sample_payload = {
            "tracking_code": "KVKK-2026-TEST01",
            "full_name": "Ahmet Yılmaz",
            "id_number": "12345678901",
            "phone": "05551112233",
            "email": "ahmet.yilmaz@test.com",
            "relationship": "Müşteri",
            "address": "İstanbul, Türkiye",
            "rights": ["Kişisel verilerimin silinmesini isteme"],
            "details": "Hesabımın ve verilerimin silinmesini talep ediyorum.",
            "response_channel": "KEP",
            "kep_address": "ahmet.yilmaz@hs01.kep.tr",
            "resolution_note": ""
        }

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO submissions (
                    tracking_code, full_name, id_number, phone, email,
                    relationship, address, rights, details, response_channel, kep_address, resolution_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample_payload["tracking_code"],
                sample_payload["full_name"],
                sample_payload["id_number"],
                sample_payload["phone"],
                sample_payload["email"],
                sample_payload["relationship"],
                sample_payload["address"],
                json.dumps(sample_payload["rights"]),
                sample_payload["details"],
                sample_payload["response_channel"],
                sample_payload["kep_address"],
                sample_payload["resolution_note"]
            ))
            conn.commit()

            cursor.execute("SELECT * FROM submissions WHERE tracking_code=?", (sample_payload["tracking_code"],))
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Kaydedilen basvuru veritabaninda sorgulanamadi.")
            self.assertEqual(row[1], "KVKK-2026-TEST01")
            self.assertEqual(row[2], "Ahmet Yılmaz")
            self.assertEqual(row[11], "ahmet.yilmaz@hs01.kep.tr")

    def test_kep_address_validator(self):
        # Geçerli KEP adresleri
        val1 = validate_kep_address("ahmet.yilmaz@hs01.kep.tr")
        self.assertTrue(val1["valid"], "Geçerli PTT KEP adresi reddedildi.")
        self.assertIn("PTT KEP", val1["provider"])

        val2 = validate_kep_address("hukuk@tnb.kep.tr")
        self.assertTrue(val2["valid"], "Geçerli TNB KEP adresi reddedildi.")
        self.assertIn("TNB", val2["provider"])

        val3 = validate_kep_address("bilgi@turkkep.kep.tr")
        self.assertTrue(val3["valid"], "Geçerli TÜRKKEP adresi reddedildi.")

        # Geçersiz KEP adresleri
        val_bad1 = validate_kep_address("deneme@gmail.com")
        self.assertFalse(val_bad1["valid"], "Normal e-posta KEP adresi olarak kabul edilmemelidir.")

        val_bad2 = validate_kep_address("")
        self.assertFalse(val_bad2["valid"], "Boş KEP adresi kabul edilmemelidir.")

        val_bad3 = validate_kep_address("ahmet.hs01.kep.tr")
        self.assertFalse(val_bad3["valid"], "@ içermeyen adres kabul edilmemelidir.")

    def test_deadline_calculation_metrics(self):
        now = datetime.datetime.now(datetime.timezone.utc)

        # Bugün açılan başvuru -> 30 gün kaldı, status 'safe'
        metrics_today = calculate_deadline_metrics(now.isoformat())
        self.assertEqual(metrics_today["days_left"], 30)
        self.assertEqual(metrics_today["status_level"], "safe")
        self.assertFalse(metrics_today["is_urgent"])

        # 20 gün önce açılan başvuru -> 10 gün kaldı, status 'warning'
        dt_warning = now - datetime.timedelta(days=20)
        metrics_warn = calculate_deadline_metrics(dt_warning.isoformat())
        self.assertEqual(metrics_warn["days_left"], 10)
        self.assertEqual(metrics_warn["status_level"], "warning")
        self.assertFalse(metrics_warn["is_urgent"])

        # 27 gün önce açılan başvuru -> 3 gün kaldı, status 'critical', is_urgent=True
        dt_critical = now - datetime.timedelta(days=27)
        metrics_crit = calculate_deadline_metrics(dt_critical.isoformat())
        self.assertEqual(metrics_crit["days_left"], 3)
        self.assertEqual(metrics_crit["status_level"], "critical")
        self.assertTrue(metrics_crit["is_urgent"])

        # 32 gün önce açılan başvuru -> Süresi dolmuş
        dt_expired = now - datetime.timedelta(days=32)
        metrics_exp = calculate_deadline_metrics(dt_expired.isoformat())
        self.assertLessEqual(metrics_exp["days_left"], 0)
        self.assertEqual(metrics_exp["status_level"], "expired")
        self.assertTrue(metrics_exp["is_urgent"])

    def test_public_status_view_and_masking(self):
        masked_name = mask_full_name("Canan Dağdeviren")
        self.assertTrue(masked_name.startswith("C"))
        self.assertIn("*", masked_name)

        row_data = {
            "tracking_code": "KVKK-2026-TEST99",
            "full_name": "Mustafa Kemal",
            "relationship": "Çalışan",
            "response_channel": "KEP",
            "status": "İnceleniyor",
            "resolution_note": "Talebiniz hukuk müşavirliğimize sevk edilmiştir.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        pub = build_public_status_view(row_data)
        self.assertEqual(pub["tracking_code"], "KVKK-2026-TEST99")
        self.assertIn("M", pub["masked_name"])
        self.assertIn("K", pub["masked_name"])
        self.assertEqual(pub["status"], "İnceleniyor")
        self.assertEqual(pub["resolution_note"], "Talebiniz hukuk müşavirliğimize sevk edilmiştir.")
        self.assertIn("days_left", pub["deadline"])

    def test_status_update_and_resolution(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO submissions (tracking_code, full_name, status, resolution_note)
                VALUES (?, ?, ?, ?)
            """, ("KVKK-2026-TEST_UPD", "Mehmet Akif", "İnceleniyor", ""))
            conn.commit()

            cursor.execute("""
                UPDATE submissions
                SET status = 'Cevaplandı', resolution_note = 'İlgili veriler KVKK Madde 7 gereği imha edilmiştir.', completed_at = CURRENT_TIMESTAMP
                WHERE tracking_code = 'KVKK-2026-TEST_UPD'
            """)
            conn.commit()

            cursor.execute("SELECT status, resolution_note, completed_at FROM submissions WHERE tracking_code = 'KVKK-2026-TEST_UPD'")
            row = cursor.fetchone()
            self.assertEqual(row[0], "Cevaplandı")
            self.assertIn("imha edilmiştir", row[1])
            self.assertIsNotNone(row[2])

    def test_files_exist(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "index.html")), "index.html eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "admin.html")), "admin.html eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "takip.html")), "takip.html eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "server.py")), "server.py eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "scripts", "kvkk_validation_engine.py")), "kvkk_validation_engine.py eksik")

if __name__ == "__main__":
    print("=" * 60)
    print("  KVKK PORTAL TEST SÜİTİ")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKVKKPortal)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("\n✅ TÜM TESTLER BAŞARIYLA GEÇTİ!")
        sys.exit(0)
    else:
        print("\n❌ TEST BAŞARISIZ!")
        sys.exit(1)
