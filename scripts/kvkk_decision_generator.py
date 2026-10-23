# -*- coding: utf-8 -*-
"""
scripts/kvkk_decision_generator.py
-----------------------------------
6698 Sayılı KVKK Madde 13/3 Uyarınca:
- Resmi Gerekçeli Karar ve Cevap Belgesi Üreticisi (A4 HTML & PDF)
- VERBİS Yıllık Uyum ve Başvuru Faaliyet Raporu Motoru
- KEP Resmi Yanıt İleti Paketi ve Delil Şablonu
- Excel Uyumlu UTF-8 BOM CSV Dışa Aktarımı
"""

import datetime
from xml.sax.saxutils import escape

DEFAULT_COMPANY = {
    "title": "KURUMSAL BİLİŞİM VE VERİ TEKNOLOJİLERİ A.Ş.",
    "vkn": "5810492810",
    "mersis": "0581049281000001",
    "address": "Bilişim Vadisi, Teknoloji Blokları No:42/A Gebze / Kocaeli",
    "kep_address": "kurumsal@hs01.kep.tr",
    "email": "kvkk@kurumsal.com.tr",
    "phone": "0850 300 40 50",
    "dpo_name": "Av. Mehmet Selim Akın",
    "dpo_title": "Veri Koruma İrtibat Kişisi / Hukuk Müşaviri"
}

def generate_decision_document_html(submission, company_info=None):
    """
    6698 sayılı Kanun m. 13/3 uyarınca ilgili kişiye tebliğ edilmek üzere
    Resmi Gerekçeli Karar ve Cevap Belgesi (A4 HTML & PDF) üretir.
    """
    comp = company_info or DEFAULT_COMPANY
    tracking_code = submission.get("tracking_code", "KVKK-2026-000000")
    created_at = str(submission.get("created_at", ""))
    date_str = created_at[:10] if len(created_at) >= 10 else datetime.date.today().strftime("%Y-%m-%d")
    today_str = datetime.date.today().strftime("%d.%m.%Y")

    status = submission.get("status", "Cevaplandı")
    resolution_note = submission.get("resolution_note") or "Talebiniz veri sorumlusu hukuk ve teknik birimlerince incelenmiş ve yasal süresi içinde gereği yerine getirilmiştir."

    # Haklar listesi
    rights_raw = submission.get("rights", [])
    if isinstance(rights_raw, str):
        try:
            import json
            rights_list = json.loads(rights_raw)
        except Exception:
            rights_list = [rights_raw]
    elif isinstance(rights_raw, list):
        rights_list = rights_raw
    else:
        rights_list = []

    rights_html = "".join([f"<li>{escape(str(r))}</li>" for r in rights_list]) if rights_list else "<li>Genel KVKK Madde 11 Kapsamında Bilgi Edinme Talebi</li>"

    # Karar türü rozeti
    if "Red" in status:
        badge_style = "background: #fee2e2; color: #b91c1c; border: 1px solid #f87171;"
        decision_label = "TALEBİN REDDİNE KARAR VERİLMİŞTİR"
    else:
        badge_style = "background: #dcfce7; color: #166534; border: 1px solid #86efac;"
        decision_label = "TALEBİN KABULÜNE VE GEREĞİNİN YAPILMASINA KARAR VERİLMİŞTİR"

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>KVKK Madde 13 Gerekçeli Karar Belgesi - {escape(tracking_code)}</title>
<style>
  * {{ box-sizing: border-box; font-family: 'Times New Roman', Times, serif; }}
  body {{ background: #f8fafc; padding: 24px 16px; color: #0f172a; margin: 0; line-height: 1.5; }}
  .toolbar {{ max-width: 820px; margin: 0 auto 16px auto; display: flex; justify-content: space-between; align-items: center; background: white; padding: 12px 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-family: sans-serif; }}
  .doc-container {{ max-width: 820px; margin: auto; background: white; border: 2px solid #0f172a; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
  .header {{ text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 20px; }}
  .header h1 {{ margin: 0; font-size: 1.25rem; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px; }}
  .header p {{ margin: 4px 0 0 0; font-size: 0.9rem; font-family: sans-serif; color: #475569; }}
  .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; font-size: 0.95rem; }}
  .meta-box {{ border: 1px solid #cbd5e1; padding: 12px; border-radius: 4px; background: #fafafa; }}
  .decision-banner {{ padding: 10px; border-radius: 6px; font-family: sans-serif; font-weight: 800; text-align: center; font-size: 0.95rem; margin-bottom: 20px; {badge_style} }}
  .section-title {{ font-size: 1rem; font-weight: bold; margin: 16px 0 6px 0; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; text-transform: uppercase; }}
  .content-text {{ font-size: 0.95rem; text-align: justify; line-height: 1.6; }}
  ul {{ margin: 6px 0 12px 20px; padding: 0; font-size: 0.92rem; }}
  .appeal-clause {{ background: #f0fdf4; border-left: 4px solid #16a34a; padding: 10px 14px; margin-top: 24px; font-size: 0.88rem; font-family: sans-serif; }}
  .signatures {{ display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px dashed #cbd5e1; }}
  .sig-block {{ width: 45%; text-align: center; font-size: 0.92rem; font-family: sans-serif; }}
  @media print {{
    body {{ background: transparent; padding: 0; }}
    .toolbar {{ display: none !important; }}
    .doc-container {{ border: none; padding: 0; box-shadow: none; max-width: 100%; }}
  }}
</style>
</head>
<body>

<div class="toolbar">
  <span style="font-weight: 700; font-size: 0.9rem;">🛡️ 6698 KVKK Md. 13/3 Gerekçeli Karar Belgesi ({escape(tracking_code)})</span>
  <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.85rem;">🖨️ Yazdır / PDF Olarak Kaydet</button>
</div>

<div class="doc-container">
  <div class="header">
    <h1>6698 SAYILI KİŞİSEL VERİLERİN KORUNMASI KANUNU (KVKK)</h1>
    <h2 style="font-size: 1.1rem; margin: 4px 0;">MADDE 13 UYARINCA İLGİLİ KİŞİ BAŞVURU CEVAP VE GEREKÇELİ KARAR BELGESİ</h2>
    <p>Belge Ref: <b>{escape(tracking_code)}</b> | Karar Tarihi: <b>{today_str}</b></p>
  </div>

  <div class="meta-grid">
    <div class="meta-box">
      <b>VERİ SORUMLUSU BİLGİLERİ:</b><br>
      <b>Unvan:</b> {escape(comp['title'])}<br>
      <b>VKN / Mersis:</b> {escape(comp['vkn'])} / {escape(comp.get('mersis', '-'))}<br>
      <b>Adres:</b> {escape(comp['address'])}<br>
      <b>KEP:</b> {escape(comp.get('kep_address', '-'))}<br>
      <b>E-Posta:</b> {escape(comp.get('email', '-'))}
    </div>
    <div class="meta-box">
      <b>BAŞVURU SAHİBİ (İLGİLİ KİŞİ):</b><br>
      <b>Adı Soyadı:</b> {escape(submission.get('full_name', 'İlgili Kişi'))}<br>
      <b>TCKN / Pasaport:</b> {escape(submission.get('id_number', 'Belirtilmedi'))}<br>
      <b>İlişki Türü:</b> {escape(submission.get('relationship', 'Müşteri / Kullanıcı'))}<br>
      <b>Cevap Kanalı:</b> {escape(submission.get('response_channel', 'E-Posta'))} {f"({escape(submission.get('kep_address',''))})" if submission.get('kep_address') else ""}<br>
      <b>Başvuru Tarihi:</b> {date_str}
    </div>
  </div>

  <div class="decision-banner">
    {decision_label}
  </div>

  <div class="section-title">1. TALEP EDİLEN HAKLAR (KVKK MADDE 11)</div>
  <ul>
    {rights_html}
  </ul>

  <div class="section-title">2. İLGİLİ KİŞİ TALEP VE AÇIKLAMA ÖZETİ</div>
  <div class="content-text" style="background:#f8fafc; padding:10px; border-radius:4px; border:1px solid #e2e8f0;">
    <i>"{escape(submission.get('details', 'Belirtilmedi'))}"</i>
  </div>

  <div class="section-title">3. VERİ SORUMLUSU DEĞERLENDİRMESİ VE GEREKÇELİ CEVABI</div>
  <div class="content-text" style="white-space: pre-wrap; padding: 4px 0;">
    {escape(resolution_note)}
  </div>

  <div class="appeal-clause">
    <b>⚖️ KİŞİSEL VERİLERİ KORUMA KURULU'NA ŞİKAYET HAKKI (KVKK Madde 14):</b><br>
    6698 sayılı Kanun'un 14'üncü maddesi uyarınca; baştan veya sonradan başvurunuzun reddedilmesi, verilen cevabın yetersiz bulunması veya yasal 30 günlük süre içinde cevap verilmemesi hallerinde (Madde 14); veri sorumlusunun cevabını öğrendiğiniz tarihten itibaren <b>otuz (30) gün</b> ve her hâlde başvuru tarihinden itibaren <b>altmış (60) gün</b> içinde Kişisel Verileri Koruma Kurulu'na şikâyette bulunma hakkınız saklıdır.
  </div>

  <div class="signatures">
    <div class="sig-block">
      <b>İLGİLİ KİŞİ</b><br>
      {escape(submission.get('full_name', 'İlgili Kişi'))}<br>
      <div style="height:40px;"></div>
      Tebellüğ / Bilgi Edinme
    </div>
    <div class="sig-block">
      <b>VERİ SORUMLUSU YETKİLİSİ</b><br>
      {escape(comp.get('dpo_name', 'Hukuk Müşavirliği'))}<br>
      <small>{escape(comp.get('dpo_title', 'Veri Koruma İrtibat Kişisi'))}</small><br>
      <div style="height:30px;"></div>
      Kaşe & E-İmza / İmza
    </div>
  </div>
</div>

</body>
</html>"""

def generate_kep_reply_package(submission, company_info=None):
    """
    KEP (Kayıtlı Elektronik Posta) üzerinden ilgili kişiye tebliğ edilmek üzere
    resmi delil ileti paketi, konu başlığı ve kriptografik hash şablonu üretir.
    """
    comp = company_info or DEFAULT_COMPANY
    tracking_code = submission.get("tracking_code", "KVKK-2026-000000")
    recipient_kep = submission.get("kep_address") or f"{submission.get('email', 'ilgilikisi').split('@')[0]}@hs01.kep.tr"
    sender_kep = comp.get("kep_address", "kurumsal@hs01.kep.tr")

    subject = f"6698 Sayılı KVKK Md. 13 Gerekçeli Başvuru Cevabı (Ref: {tracking_code})"
    
    body = f"""Sayın {submission.get('full_name', 'İlgili Kişi')},

Şirketimize '{tracking_code}' takip numarası ile iletmiş olduğunuz 6698 sayılı Kişisel Verilerin Korunması Kanunu'nun (KVKK) 11. maddesi kapsamındaki başvurunuz, Veri Sorumlusu bünyesinde incelenmiştir.

Kanun'un 13. maddesinin 3. fıkrası uyarınca hazırlanan resmi Gerekçeli Karar ve Cevap Belgesi ekte yer almakta olup, Kayıtlı Elektronik Posta (KEP) adresinize resmi olarak tebliğ edilmiştir.

Karar Özeti:
--------------------------------------------------
Takip No       : {tracking_code}
Başvuru Sahibi : {submission.get('full_name')}
Karar Durumu   : {submission.get('status', 'Cevaplandı')}
Gerekçeli Not  : {submission.get('resolution_note', 'Talebiniz sonuçlandırılmıştır.')}
--------------------------------------------------

Kanun'un 14. maddesi gereğince Kişisel Verileri Koruma Kurulu'na şikayet hakkınız yasal süresi içinde saklıdır.

Bilgilerinize sunarız.

Saygılarımızla,
{comp.get('title')}
Veri Sorumlusu İrtibat Kişisi: {comp.get('dpo_name')}
Tel: {comp.get('phone')}
"""

    return {
        "status": "ready",
        "tracking_code": tracking_code,
        "sender_kep": sender_kep,
        "recipient_kep": recipient_kep,
        "subject": subject,
        "body": body,
        "legal_basis": "KVKK Madde 13/3 & TTK Madde 18/3 KEP Resmi Tebligat"
    }

def calculate_verbis_report(submissions):
    """
    Şirketin VERBİS ve Yıllık KVKK Faaliyet Denetimleri için istatistiki metrikler çıkarır.
    """
    total = len(submissions)
    if total == 0:
        return {
            "total_count": 0,
            "answered_count": 0,
            "in_progress_count": 0,
            "rejected_count": 0,
            "on_time_count": 0,
            "on_time_pct": 100.0,
            "relationship_breakdown": {},
            "channel_breakdown": {},
            "top_rights": {}
        }

    answered = 0
    in_progress = 0
    rejected = 0
    on_time = 0

    rel_counts = {}
    channel_counts = {}
    rights_counts = {}

    for s in submissions:
        st = s.get("status", "İnceleniyor")
        if "Cevap" in st or "Tamam" in st:
            answered += 1
            on_time += 1 # 30 gün içinde sonuçlandırıldı
        elif "Red" in st:
            rejected += 1
            on_time += 1
        else:
            in_progress += 1
            # Süresi geçip geçmediğini kontrol et
            from scripts.kvkk_validation_engine import calculate_deadline_metrics
            dm = calculate_deadline_metrics(s.get("created_at"))
            if dm["days_left"] > 0:
                on_time += 1

        rel = s.get("relationship") or "Diğer"
        rel_counts[rel] = rel_counts.get(rel, 0) + 1

        chan = s.get("response_channel") or "E-Posta"
        channel_counts[chan] = channel_counts.get(chan, 0) + 1

        r_raw = s.get("rights") or []
        if isinstance(r_raw, str):
            try:
                import json
                r_list = json.loads(r_raw)
            except Exception:
                r_list = [r_raw]
        else:
            r_list = r_raw if isinstance(r_raw, list) else []

        for r in r_list:
            rights_counts[r] = rights_counts.get(r, 0) + 1

    return {
        "total_count": total,
        "answered_count": answered,
        "in_progress_count": in_progress,
        "rejected_count": rejected,
        "on_time_count": on_time,
        "on_time_pct": round((on_time / total) * 100.0, 1),
        "relationship_breakdown": rel_counts,
        "channel_breakdown": channel_counts,
        "top_rights": rights_counts
    }

def generate_verbis_report_html(submissions, company_info=None):
    """
    A4 formatında yazdırılabilir Yıllık VERBİS ve KVKK Başvuru Faaliyet Raporu (HTML).
    """
    comp = company_info or DEFAULT_COMPANY
    verbis = calculate_verbis_report(submissions)
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    year = datetime.date.today().year

    # Haklar dökümü satırları
    rights_rows = []
    for r_name, count in sorted(verbis["top_rights"].items(), key=lambda x: x[1], reverse=True):
        rights_rows.append(f"""
        <tr>
            <td>{escape(str(r_name))}</td>
            <td style="text-align:center; font-weight:bold;">{count}</td>
            <td style="text-align:right;">%{count/verbis['total_count']*100:.1f}</td>
        </tr>
        """)
    rights_tbody = "\n".join(rights_rows) if rights_rows else "<tr><td colspan='3' style='text-align:center;'>Kayıt yok</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>VERBİS & KVKK Başvuru Faaliyet Raporu - {year}</title>
<style>
  * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  body {{ background: #f8fafc; padding: 24px 16px; color: #0f172a; margin: 0; }}
  .toolbar {{ max-width: 900px; margin: 0 auto 16px auto; display: flex; justify-content: space-between; align-items: center; background: white; padding: 12px 20px; border-radius: 8px; border: 1px solid #cbd5e1; }}
  .container {{ max-width: 900px; margin: auto; background: white; border: 1px solid #cbd5e1; padding: 36px; border-radius: 8px; }}
  .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0f172a; padding-bottom: 14px; margin-bottom: 24px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }}
  .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; border-left: 4px solid #2563eb; text-align: center; }}
  .kpi-val {{ font-size: 1.8rem; font-weight: 800; color: #0f172a; margin-top: 4px; }}
  .kpi-lbl {{ font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 700; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.88rem; }}
  th, td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; }}
  th {{ background: #0f172a; color: white; font-size: 0.75rem; text-transform: uppercase; }}
  @media print {{
    body {{ background: transparent; padding: 0; }}
    .toolbar {{ display: none !important; }}
    .container {{ border: none; padding: 0; }}
  }}
</style>
</head>
<body>

<div class="toolbar">
  <span style="font-weight: 700; font-size: 0.95rem;">📊 VERBİS & Yıllık KVKK Başvuru Faaliyet Raporu</span>
  <div style="display: flex; gap: 8px;">
    <a href="/api/export-csv" style="background: #10b981; color: white; text-decoration: none; padding: 8px 14px; border-radius: 6px; font-weight: bold; font-size: 0.85rem;">📥 CSV İndir</a>
    <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.85rem;">🖨️ Yazdır / PDF</button>
  </div>
</div>

<div class="container">
  <div class="header">
    <div>
      <h1 style="margin:0; font-size:1.3rem; text-transform:uppercase;">YILLIK KVKK & VERBİS BAŞVURU UYUM RAPORU</h1>
      <p style="margin:4px 0 0 0; color:#64748b; font-size:0.9rem;">Veri Sorumlusu: <b>{escape(comp['title'])}</b> | Tarih: {today_str}</p>
    </div>
    <div style="text-align: right; font-size: 0.85rem;">
      <b>Dönem:</b> {year} Takvim Yılı<br>
      <b>VKN:</b> {escape(comp['vkn'])}
    </div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-lbl">Toplam Başvuru</div>
      <div class="kpi-val">{verbis['total_count']}</div>
    </div>
    <div class="kpi-card" style="border-left-color: #10b981;">
      <div class="kpi-lbl">Sonuçlandırılan (Cevaplanan)</div>
      <div class="kpi-val" style="color: #10b981;">{verbis['answered_count']}</div>
    </div>
    <div class="kpi-card" style="border-left-color: #f59e0b;">
      <div class="kpi-lbl">İncelenmekte Olan</div>
      <div class="kpi-val" style="color: #f59e0b;">{verbis['in_progress_count']}</div>
    </div>
    <div class="kpi-card" style="border-left-color: #16a34a;">
      <div class="kpi-lbl">30 Güne Uyum Oranı</div>
      <div class="kpi-val" style="color: #16a34a;">%{verbis['on_time_pct']}</div>
    </div>
  </div>

  <h3 style="font-size:0.95rem; text-transform:uppercase; margin-bottom:8px;">Madde 11 Kapsamında Talep Edilen Hak Dağılımı</h3>
  <table>
    <thead>
      <tr>
        <th>Talep Edilen Hak Konusu</th>
        <th style="width: 100px; text-align: center;">Adet</th>
        <th style="width: 100px; text-align: right;">Oran</th>
      </tr>
    </thead>
    <tbody>
      {rights_tbody}
    </tbody>
  </table>

  <div style="font-size: 0.82rem; color: #475569; background: #f8fafc; padding: 12px; border-left: 3px solid #2563eb; border-radius: 4px; margin-top: 24px;">
    <b>YASAL DENETİM NOTU:</b><br>
    İşbu rapor, 6698 sayılı Kişisel Verilerin Korunması Kanunu ve Veri Sorumluları Sicili Hakkında Yönetmelik gereğince kurum içi periyodik uyum denetimleri ve Kişisel Verileri Koruma Kurumu denetimlerine ibraz edilmek üzere üretilmiştir.
  </div>
</div>

</body>
</html>"""

def generate_kvkk_csv_export(submissions):
    """
    Excel uyumlu UTF-8 with BOM formatında CSV başvuru listesi üretir.
    """
    lines = [
        "Takip Kodu;Basvuru Tarihi;Ad Soyad;TCKN/Kimlik;Telefon;E-Posta;Iliski;Cevap Kanali;KEP Adresi;Talep Konulari;Durum;Kalan Gun;Cozum Notu"
    ]

    for s in submissions:
        code = str(s.get("tracking_code", "")).replace(";", " ")
        date_str = str(s.get("created_at", "")).replace(";", " ")
        name = str(s.get("full_name", "")).replace(";", " ")
        id_num = str(s.get("id_number", "")).replace(";", " ")
        phone = str(s.get("phone", "")).replace(";", " ")
        email = str(s.get("email", "")).replace(";", " ")
        rel = str(s.get("relationship", "")).replace(";", " ")
        chan = str(s.get("response_channel", "")).replace(";", " ")
        kep = str(s.get("kep_address", "")).replace(";", " ")
        rights = str(s.get("rights", "")).replace(";", " ").replace('"', "'")
        status = str(s.get("status", "")).replace(";", " ")
        note = str(s.get("resolution_note", "")).replace(";", " ").replace("\n", " ")

        from scripts.kvkk_validation_engine import calculate_deadline_metrics
        dm = calculate_deadline_metrics(s.get("created_at"))
        days_left = dm["days_left"]

        row = f'"{code}";"{date_str}";"{name}";"{id_num}";"{phone}";"{email}";"{rel}";"{chan}";"{kep}";"{rights}";"{status}";{days_left};"{note}"'
        lines.append(row)

    return "\ufeff" + "\n".join(lines)
