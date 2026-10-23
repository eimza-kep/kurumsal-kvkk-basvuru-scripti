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
6. KVKK Md. 13/3 Gerekçeli Karar Belgesi (A4 HTML & PDF)
7. VERBİS Yıllık Uyum Raporu & KEP Yanıt Şablonu
8. Excel uyumlu UTF-8 BOM CSV Dışa Aktarımı
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
from scripts.kvkk_decision_generator import (
    generate_decision_document_html,
    generate_kep_reply_package,
    calculate_verbis_report,
    generate_verbis_report_html,
    generate_kvkk_csv_export,
    DEFAULT_COMPANY
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
        val1 = validate_kep_address("ahmet.yilmaz@hs01.kep.tr")
        self.assertTrue(val1["valid"], "Geçerli PTT KEP adresi reddedildi.")
        self.assertIn("PTT KEP", val1["provider"])

        val2 = validate_kep_address("hukuk@tnb.kep.tr")
        self.assertTrue(val2["valid"], "Geçerli TNB KEP adresi reddedildi.")
        self.assertIn("TNB", val2["provider"])

        val3 = validate_kep_address("bilgi@turkkep.kep.tr")
        self.assertTrue(val3["valid"], "Geçerli TÜRKKEP adresi reddedildi.")

        val_bad1 = validate_kep_address("deneme@gmail.com")
        self.assertFalse(val_bad1["valid"], "Normal e-posta KEP adresi olarak kabul edilmemelidir.")

        val_bad2 = validate_kep_address("")
        self.assertFalse(val_bad2["valid"], "Boş KEP adresi kabul edilmemelidir.")

        val_bad3 = validate_kep_address("ahmet.hs01.kep.tr")
        self.assertFalse(val_bad3["valid"], "@ içermeyen adres kabul edilmemelidir.")

    def test_deadline_calculation_metrics(self):
        now = datetime.datetime.now(datetime.timezone.utc)

        metrics_today = calculate_deadline_metrics(now.isoformat())
        self.assertEqual(metrics_today["days_left"], 30)
        self.assertEqual(metrics_today["status_level"], "safe")
        self.assertFalse(metrics_today["is_urgent"])

        dt_warning = now - datetime.timedelta(days=20)
        metrics_warn = calculate_deadline_metrics(dt_warning.isoformat())
        self.assertEqual(metrics_warn["days_left"], 10)
        self.assertEqual(metrics_warn["status_level"], "warning")
        self.assertFalse(metrics_warn["is_urgent"])

        dt_critical = now - datetime.timedelta(days=27)
        metrics_crit = calculate_deadline_metrics(dt_critical.isoformat())
        self.assertEqual(metrics_crit["days_left"], 3)
        self.assertEqual(metrics_crit["status_level"], "critical")
        self.assertTrue(metrics_crit["is_urgent"])

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

    def test_decision_document_html_generation(self):
        submission_sample = {
            "tracking_code": "KVKK-2026-TEST-DEC",
            "full_name": "Zeynep Korkmaz",
            "id_number": "98765432101",
            "relationship": "Müşteri",
            "response_channel": "KEP",
            "kep_address": "zeynep@hs01.kep.tr",
            "rights": ["Kişisel verilerimin işlenip işlenmediğini öğrenme", "Eksik veya yanlış işlenmişse düzeltilmesini isteme"],
            "details": "Adres bilgilerimin güncellenmesini ve pazarlama listelerinden çıkarılmamı talep ediyorum.",
            "status": "Cevaplandı",
            "resolution_note": "Talebiniz doğrultusunda iletişim adresiniz güncellenmiş ve ticari ileti onayınız iptal edilmiştir.",
            "created_at": "2026-10-01T10:00:00Z"
        }

        html = generate_decision_document_html(submission_sample)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("KVKK-2026-TEST-DEC", html)
        self.assertIn("MADDE 13 UYARINCA İLGİLİ KİŞİ BAŞVURU CEVAP VE GEREKÇELİ KARAR BELGESİ", html)
        self.assertIn("Zeynep Korkmaz", html)
        self.assertIn("TALEBİN KABULÜNE VE GEREĞİNİN YAPILMASINA KARAR VERİLMİŞTİR", html)
        self.assertIn("Madde 14", html, "Kurul'a şikayet hakkı (KVKK m. 14) yer almalıdır.")
        self.assertIn("zeynep@hs01.kep.tr", html)

    def test_kep_reply_package(self):
        submission_sample = {
            "tracking_code": "KVKK-2026-TEST-KEPPKG",
            "full_name": "Hasan Tahsin",
            "email": "hasan@test.com",
            "kep_address": "hasan@hs01.kep.tr",
            "status": "Cevaplandı",
            "resolution_note": "Verileriniz imha edilmiştir."
        }
        pkg = generate_kep_reply_package(submission_sample)
        self.assertEqual(pkg["status"], "ready")
        self.assertIn("KVKK-2026-TEST-KEPPKG", pkg["subject"])
        self.assertEqual(pkg["recipient_kep"], "hasan@hs01.kep.tr")
        self.assertIn("Hasan Tahsin", pkg["body"])
        self.assertIn("KVKK Madde 13/3", pkg["legal_basis"])

    def test_verbis_report_and_html(self):
        submissions_sample = [
            {
                "tracking_code": "KVKK-TEST-V1",
                "status": "Cevaplandı",
                "relationship": "Müşteri",
                "response_channel": "KEP",
                "rights": ["Veri Silme"],
                "created_at": "2026-10-10 10:00:00"
            },
            {
                "tracking_code": "KVKK-TEST-V2",
                "status": "Reddedildi",
                "relationship": "Çalışan",
                "response_channel": "E-Posta",
                "rights": ["Veri Düzeltme"],
                "created_at": "2026-10-12 10:00:00"
            },
            {
                "tracking_code": "KVKK-TEST-V3",
                "status": "İnceleniyor",
                "relationship": "Müşteri",
                "response_channel": "E-Posta",
                "rights": ["Bilgi Alma"],
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        ]

        metrics = calculate_verbis_report(submissions_sample)
        self.assertEqual(metrics["total_count"], 3)
        self.assertEqual(metrics["answered_count"], 1)
        self.assertEqual(metrics["rejected_count"], 1)
        self.assertEqual(metrics["in_progress_count"], 1)
        self.assertEqual(metrics["on_time_pct"], 100.0)
        self.assertEqual(metrics["relationship_breakdown"]["Müşteri"], 2)

        html = generate_verbis_report_html(submissions_sample)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("YILLIK KVKK & VERBİS BAŞVURU UYUM RAPORU", html)
        self.assertIn("Veri Silme", html)

    def test_kvkk_csv_export(self):
        submissions_sample = [
            {
                "tracking_code": "KVKK-TEST-CSV1",
                "full_name": "Banu Avar",
                "id_number": "11122233344",
                "phone": "05554443322",
                "email": "banu@test.com",
                "relationship": "Müşteri",
                "response_channel": "KEP",
                "kep_address": "banu@hs01.kep.tr",
                "rights": ["Veri Silme"],
                "status": "Cevaplandı",
                "resolution_note": "Talebiniz onaylandı",
                "created_at": "2026-10-15 12:00:00"
            }
        ]
        csv_text = generate_kvkk_csv_export(submissions_sample)
        self.assertTrue(csv_text.startswith("\ufeff"), "Excel uyumu için UTF-8 BOM ile başlamalıdır.")
        self.assertIn("KVKK-TEST-CSV1", csv_text)
        self.assertIn("Banu Avar", csv_text)
        self.assertIn("banu@hs01.kep.tr", csv_text)

    def test_files_exist(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "index.html")), "index.html eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "admin.html")), "admin.html eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "takip.html")), "takip.html eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "server.py")), "server.py eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "scripts", "kvkk_validation_engine.py")), "kvkk_validation_engine.py eksik")
        self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, "scripts", "kvkk_decision_generator.py")), "kvkk_decision_generator.py eksik")

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
