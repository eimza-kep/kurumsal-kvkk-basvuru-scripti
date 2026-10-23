# -*- coding: utf-8 -*-
"""
kvkk_validation_engine.py
-------------------------
6698 Sayılı KVKK Uyum ve Doğrulama Motoru.
- KEP (Kayıtlı Elektronik Posta) adres formatı ve BTK KEPHS sağlayıcı denetimi.
- 30 günlük yasal cevap verme süresi sayacı ve acil durum seviyelendirmesi.
- İlgili kişi durum sorgulama için güvenli maskelenmiş veri üretimi.
"""

import re
import datetime
from typing import Dict, Any, Optional

# BTK Onaylı Kayıtlı Elektronik Posta Hizmet Sağlayıcıları (KEPHS) Domainleri
RECOGNIZED_KEP_DOMAINS = [
    "hs01.kep.tr",
    "hs02.kep.tr",
    "hs03.kep.tr",
    "hs04.kep.tr",
    "hs05.kep.tr",
    "hs06.kep.tr",
    "hs07.kep.tr",
    "hs08.kep.tr",
    "hs09.kep.tr",
    "tnb.kep.tr",
    "turkkep.kep.tr",
    "e-tugra.kep.tr",
    "kepanadolu.kep.tr"
]

def validate_kep_address(kep: Optional[str]) -> Dict[str, Any]:
    """
    KEP adresinin BTK standartlarına ve genel KEP formatına uygunluğunu denetler.
    Örnek geçerli: ahmet.yilmaz@hs01.kep.tr, sirket@hs02.kep.tr, avukat@tnb.kep.tr
    """
    if not kep or not isinstance(kep, str):
        return {
            "valid": False,
            "code": "EMPTY",
            "message": "KEP adresi boş bırakılamaz."
        }

    kep = kep.strip().lower()

    # Temel e-posta deseni
    kep_regex = r"^[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9_\.\-]+\.kep\.tr$"
    if not re.match(kep_regex, kep):
        return {
            "valid": False,
            "code": "INVALID_FORMAT",
            "message": "Geçersiz KEP formatı. KEP adresi '.kep.tr' uzantılı olmalıdır (Örn: ad.soyad@hs01.kep.tr)."
        }

    parts = kep.split("@")
    if len(parts) != 2:
        return {
            "valid": False,
            "code": "INVALID_STRUCTURE",
            "message": "KEP adresi tam bir '@' kullanıcı ve alan adı yapısına sahip olmalıdır."
        }

    local_part, domain_part = parts[0], parts[1]

    if len(local_part) < 2:
        return {
            "valid": False,
            "code": "SHORT_LOCAL_PART",
            "message": "KEP kullanıcı adı en az 2 karakter olmalıdır."
        }

    # Bilinen yetkili KEPHS kontrolü
    is_recognized_provider = any(domain_part == recognized or domain_part.endswith("." + recognized) for recognized in RECOGNIZED_KEP_DOMAINS)

    provider_name = "Yetkili KEPHS"
    if "tnb" in domain_part:
        provider_name = "TNB KEP (Türkiye Noterler Birliği)"
    elif "turkkep" in domain_part:
        provider_name = "TÜRKKEP A.Ş."
    elif "hs0" in domain_part:
        provider_name = "PTT KEP / Kurumsal KEPHS"
    elif "e-tugra" in domain_part:
        provider_name = "E-Tuğra KEP"

    return {
        "valid": True,
        "code": "OK",
        "kep_address": kep,
        "domain": domain_part,
        "provider": provider_name,
        "is_official_provider": is_recognized_provider,
        "message": f"Geçerli KEP Adresi ({provider_name})."
    }

def calculate_deadline_metrics(created_at: Any) -> Dict[str, Any]:
    """
    KVKK Madde 13/2 gereğince 30 günlük yasal süre sayacını hesaplar.
    Dönen alanlar:
    - total_days: 30
    - elapsed_days: Geçen gün sayısı
    - days_left: Kalan gün sayısı
    - status_level: 'safe' (>15 gün), 'warning' (6-15 gün), 'critical' (1-5 gün), 'expired' (<=0 gün)
    - color: hex kod
    """
    if isinstance(created_at, str):
        # Desteklenen formatlar: ISO veya SQLite default CURRENT_TIMESTAMP
        clean_str = created_at.replace("Z", "+00:00")
        try:
            if "T" in clean_str:
                dt = datetime.datetime.fromisoformat(clean_str)
            else:
                dt = datetime.datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                dt = datetime.datetime.fromisoformat(clean_str.split(".")[0])
            except Exception:
                dt = datetime.datetime.now(datetime.timezone.utc)
    elif isinstance(created_at, (datetime.datetime, datetime.date)):
        dt = created_at if isinstance(created_at, datetime.datetime) else datetime.datetime.combine(created_at, datetime.time.min)
    else:
        dt = datetime.datetime.now(datetime.timezone.utc)

    now = datetime.datetime.now(datetime.timezone.utc)
    # Farkı gün cinsinden bul
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    diff_seconds = (now - dt).total_seconds()
    elapsed_days = max(0, int(diff_seconds // 86400))
    days_left = 30 - elapsed_days

    deadline_date = dt + datetime.timedelta(days=30)
    deadline_str = deadline_date.strftime("%d.%m.%Y")

    if days_left <= 0:
        status_level = "expired"
        badge_text = "🚨 Yasal Süre Doldu!"
        color = "#b91c1c"
        is_urgent = True
    elif days_left <= 5:
        status_level = "critical"
        badge_text = f"🚨 Kritik: {days_left} Gün Kaldı"
        color = "#dc2626"
        is_urgent = True
    elif days_left <= 15:
        status_level = "warning"
        badge_text = f"⚠️ {days_left} Gün Kaldı"
        color = "#b45309"
        is_urgent = False
    else:
        status_level = "safe"
        badge_text = f"⏳ {days_left} Gün Kaldı"
        color = "#15803d"
        is_urgent = False

    return {
        "elapsed_days": elapsed_days,
        "days_left": days_left,
        "deadline_date": deadline_str,
        "status_level": status_level,
        "badge_text": badge_text,
        "color": color,
        "is_urgent": is_urgent
    }

def mask_text(val: Optional[str], show_start: int = 2, show_end: int = 2) -> str:
    """Metni KVKK gizliliğine uygun şekilde maskeler (Örn: Ah*** Yı***)."""
    if not val:
        return "***"
    val = str(val).strip()
    if len(val) <= show_start + show_end:
        return "*" * len(val)
    return val[:show_start] + ("*" * (len(val) - show_start - show_end)) + val[-show_end:]

def mask_full_name(name: Optional[str]) -> str:
    """İsim ve soyismin ilk harflerini gösterip maskeler (Örn: A*** Y***)."""
    if not name:
        return "***"
    parts = name.strip().split()
    masked_parts = []
    for p in parts:
        if len(p) > 1:
            masked_parts.append(p[0] + ("*" * (len(p) - 1)))
        else:
            masked_parts.append(p)
    return " ".join(masked_parts)

def build_public_status_view(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    İlgili kişinin durum sorgulama sayfasında göreceği güvenli
    maskelenmiş durum ve süre özetini üretir.
    """
    deadline = calculate_deadline_metrics(row.get("created_at"))
    
    return {
        "tracking_code": row.get("tracking_code"),
        "masked_name": mask_full_name(row.get("full_name")),
        "relationship": row.get("relationship"),
        "response_channel": row.get("response_channel"),
        "status": row.get("status", "İnceleniyor"),
        "resolution_note": row.get("resolution_note") or "",
        "created_at": str(row.get("created_at", "")),
        "deadline": deadline
    }
