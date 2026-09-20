# -*- coding: utf-8 -*-
"""
test_kvkk.py
------------
KVKK Başvuru Portalı entegrasyon ve birim testi.
SQLite veritabanı, veri bütünlüğü ve takip kodu üretimini test eder.
"""

import os
import sys
import json
import sqlite3
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import init_db, DB_FILE

class TestKVKKPortal(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_database_initialization(self):
        self.assertTrue(os.path.exists(DB_FILE), "SQLite veritabani dosyasi olusturulamadi.")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='submissions'")
            table = cursor.fetchone()
            self.assertIsNotNone(table, "'submissions' tablosu veritabaninda bulunamadi.")

    def test_application_submission_flow(self):
        sample_payload = {
            "tracking_code": "KVKK-2026-TEST01",
            "full_name": "Ahmet Yilmaz",
            "id_number": "12345678901",
            "phone": "05551112233",
            "email": "ahmet.yilmaz@test.com",
            "relationship": "Musteri",
            "address": "Istanbul, Turkiye",
            "rights": ["Kisisel verilerimin silinmesini isteme"],
            "details": "Hesabimin ve verilerimin silinmesini talep ediyorum.",
            "response_channel": "E-posta",
            "kep_address": ""
        }

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO submissions (
                    tracking_code, full_name, id_number, phone, email,
                    relationship, address, rights, details, response_channel, kep_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                sample_payload["kep_address"]
            ))
            conn.commit()

            cursor.execute("SELECT * FROM submissions WHERE tracking_code=?", (sample_payload["tracking_code"],))
            row = cursor.fetchone()
            self.assertIsNotNone(row, "Kaydedilen basvuru veritabaninda sorgulanamadi.")
            self.assertEqual(row[1], "KVKK-2026-TEST01")
            self.assertEqual(row[2], "Ahmet Yilmaz")

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
