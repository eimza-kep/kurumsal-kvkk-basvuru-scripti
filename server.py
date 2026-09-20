# -*- coding: utf-8 -*-
"""
server.py
---------
6698 KVKK İlgili Kişi Başvuru Portalı - Sıfır Bağımlılıklı Python Sunucusu.
Yerleşik SQLite veritabanı ile başvuruları güvenle depolar.
"""

import os
import sys
import json
import sqlite3
import random
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Windows console UTF-8 desteği
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 8080
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kvkk_submissions.db")

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_code TEXT UNIQUE,
                full_name TEXT,
                id_number TEXT,
                phone TEXT,
                email TEXT,
                relationship TEXT,
                address TEXT,
                rights TEXT,
                details TEXT,
                response_channel TEXT,
                kep_address TEXT,
                status TEXT DEFAULT 'İnceleniyor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

class KVKKHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "kvkk-portal"}).encode("utf-8"))
            return

        if parsed.path == "/api/list":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            with sqlite3.connect(DB_FILE) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM submissions ORDER BY created_at DESC")
                rows = [dict(r) for r in cursor.fetchall()]
                for r in rows:
                    if r.get("rights"):
                        try:
                            r["rights"] = json.loads(r["rights"])
                        except Exception:
                            pass
                self.wfile.write(json.dumps(rows, ensure_ascii=False).encode("utf-8"))
            return

        # Statik dosya sunumu
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
            except Exception:
                data = {}

            tracking_code = f"KVKK-2026-{random.randint(100000, 999999)}"
            rights_json = json.dumps(data.get("rights", []), ensure_ascii=False)

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO submissions (
                        tracking_code, full_name, id_number, phone, email,
                        relationship, address, rights, details, response_channel,
                        kep_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tracking_code,
                    data.get("full_name", ""),
                    data.get("id_number", ""),
                    data.get("phone", ""),
                    data.get("email", ""),
                    data.get("relationship", ""),
                    data.get("address", ""),
                    rights_json,
                    data.get("details", ""),
                    data.get("response_channel", ""),
                    data.get("kep_address", "")
                ))
                conn.commit()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            resp = {
                "success": True,
                "tracking_code": tracking_code,
                "message": "KVKK başvurunuz yasal olarak kaydedilmiştir."
            }
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server(port=PORT):
    init_db()
    server_address = ("", port)
    httpd = HTTPServer(server_address, KVKKHandler)
    print(f"🛡️ KVKK Başvuru Portalı aktif: http://localhost:{port}")
    print(f"📋 Admin Paneli: http://localhost:{port}/admin.html")
    httpd.serve_forever()

if __name__ == "__main__":
    init_db()
    run_server()
