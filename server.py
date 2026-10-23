# -*- coding: utf-8 -*-
"""
server.py
---------
6698 KVKK İlgili Kişi Başvuru Portalı - Sıfır Bağımlılıklı Python Sunucusu.
Yerleşik SQLite veritabanı ile başvuruları güvenle depolar.
- 30 günlük yasal süre sayacı ve acil uyarı motoru
- KEP adresi formatı ve BTK doğrulayıcısı
- KVKK Md. 11/13 başvuru durum sorgulama portalı (/takip)
"""

import os
import sys
import json
import sqlite3
import random
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Windows console UTF-8 desteği
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scripts.kvkk_validation_engine import (
    validate_kep_address,
    calculate_deadline_metrics,
    build_public_status_view
)

PORT = int(os.environ.get("PORT", 8080))
DB_FILE = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "kvkk_submissions.db"))

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
                resolution_note TEXT DEFAULT '',
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Mevcut veritabanlarında eksik kolon varsa dinamik ekle
        cursor.execute("PRAGMA table_info(submissions)")
        columns = [row[1] for row in cursor.fetchall()]
        if "resolution_note" not in columns:
            cursor.execute("ALTER TABLE submissions ADD COLUMN resolution_note TEXT DEFAULT ''")
        if "completed_at" not in columns:
            cursor.execute("ALTER TABLE submissions ADD COLUMN completed_at TIMESTAMP")
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

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path in ("/takip", "/takip/"):
            self.path = "/takip.html"
            return super().do_GET()

        if parsed.path in ("/admin", "/admin/"):
            self.path = "/admin.html"
            return super().do_GET()

        if parsed.path == "/health":
            self.send_json({"status": "healthy", "service": "kvkk-portal"})
            return

        if parsed.path == "/api/validate-kep":
            kep_candidate = qs.get("kep", [""])[0]
            val_res = validate_kep_address(kep_candidate)
            self.send_json(val_res)
            return

        if parsed.path == "/api/list":
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
                    r["deadline_metrics"] = calculate_deadline_metrics(r.get("created_at"))
                self.send_json(rows)
            return

        # Statik dosya sunumu
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if parsed.path == "/api/submit":
            channel = data.get("response_channel", "")
            kep_addr = data.get("kep_address", "").strip()

            # KEP seçilmişse veya KEP adresi girilmişse doğrula
            if channel == "KEP" or kep_addr:
                if channel == "KEP" and not kep_addr:
                    self.send_json({
                        "success": False,
                        "error": "Cevap kanalı olarak KEP seçildiğinde geçerli bir KEP adresi girilmelidir."
                    }, status=400)
                    return
                if kep_addr:
                    val = validate_kep_address(kep_addr)
                    if not val["valid"]:
                        self.send_json({
                            "success": False,
                            "error": f"Geçersiz KEP Adresi: {val['message']}"
                        }, status=400)
                        return

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
                    channel,
                    kep_addr
                ))
                conn.commit()

            deadline = calculate_deadline_metrics(data.get("created_at"))
            resp = {
                "success": True,
                "tracking_code": tracking_code,
                "message": "KVKK başvurunuz yasal olarak kaydedilmiştir.",
                "deadline": deadline
            }
            self.send_json(resp)
            return

        if parsed.path == "/api/track":
            tracking_code = data.get("tracking_code", "").strip()
            id_verify = data.get("id_verify", "").strip()

            if not tracking_code:
                self.send_json({"success": False, "error": "Lütfen başvuru takip kodunu giriniz."}, status=400)
                return

            with sqlite3.connect(DB_FILE) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM submissions WHERE tracking_code = ?", (tracking_code,))
                row = cursor.fetchone()

            if not row:
                self.send_json({
                    "success": False,
                    "error": f"'{tracking_code}' numaralı başvuru bulunamadı. Lütfen takip kodunuzu kontrol ediniz."
                }, status=404)
                return

            row_dict = dict(row)
            # Kimlik doğrulaması kontrolü (isteğe bağlı güvenlik katmanı: TCKN son 4 hanesi veya tam TCKN)
            if id_verify:
                clean_target = row_dict.get("id_number", "").strip()
                if not (clean_target.endswith(id_verify) or clean_target == id_verify):
                    self.send_json({
                        "success": False,
                        "error": "Girdiğiniz kimlik doğrulama bilgisi başvuru kaydı ile uyuşmuyor."
                    }, status=403)
                    return

            public_view = build_public_status_view(row_dict)
            self.send_json({"success": True, "data": public_view})
            return

        if parsed.path == "/api/status":
            tracking_code = data.get("tracking_code", "").strip()
            new_status = data.get("status", "").strip()
            resolution_note = data.get("resolution_note", "").strip()

            if not tracking_code or not new_status:
                self.send_json({"success": False, "error": "Eksik parametreler."}, status=400)
                return

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                if new_status == "Cevaplandı":
                    cursor.execute("""
                        UPDATE submissions
                        SET status = ?, resolution_note = ?, completed_at = CURRENT_TIMESTAMP
                        WHERE tracking_code = ?
                    """, (new_status, resolution_note, tracking_code))
                else:
                    cursor.execute("""
                        UPDATE submissions
                        SET status = ?, resolution_note = ?
                        WHERE tracking_code = ?
                    """, (new_status, resolution_note, tracking_code))
                conn.commit()

            self.send_json({
                "success": True,
                "tracking_code": tracking_code,
                "status": new_status,
                "message": "Başvuru durumu başarıyla güncellendi."
            })
            return

        self.send_response(404)
        self.end_headers()

def run_server(port=PORT):
    init_db()
    server_address = ("", port)
    httpd = HTTPServer(server_address, KVKKHandler)
    print(f"🛡️ KVKK Başvuru Portalı aktif: http://localhost:{port}")
    print(f"🔍 Durum Sorgulama: http://localhost:{port}/takip")
    print(f"📋 Admin Paneli: http://localhost:{port}/admin.html")
    httpd.serve_forever()

if __name__ == "__main__":
    init_db()
    run_server()
