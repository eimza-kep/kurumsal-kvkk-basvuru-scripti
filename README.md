# 🛡️ 6698 KVKK İlgili Kişi Başvuru Scripti, Takip Portalı & Çerez Yönetimi

[![CI Test Suite](https://github.com/eimza-kep/kurumsal-kvkk-basvuru-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kurumsal-kvkk-basvuru-scripti/actions/workflows/ci.yml)
[![Canlı Demo](https://img.shields.io/badge/Demo-Canl%C4%B1%20Test%20Et-brightgreen.svg)](https://eimza-kep.github.io/kurumsal-kvkk-basvuru-scripti/)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

Türkiye'de faaliyet gösteren şirketler, e-ticaret siteleri, avukatlar, mali müşavirler, sağlık kuruluşları ve KOBİ'lerin web sitelerine **1 dakikada kurup çalıştırabileceği**, 6698 sayılı Kişisel Verilerin Korunması Kanunu'na tam uyumlu **İlgili Kişi (Veri Sahibi) Başvuru Formu**, **Başvuru Durum Sorgulama Portalı (`/takip`)**, **30 Günlük Yasal Cevap Süresi Sayacı & Alarm Sistemi**, **KEP Adresi Doğrulayıcısı**, **Yönetim Paneli** ve **Çerez İzin Barı**.

---

## 🌟 Temel Yetenekler ve Yenilikler

### 1. ⏱️ 30 Günlük Yasal Cevap Verme Süresi Sayacı ve Acil Bildirim Sistemi (KVKK Md. 13/2)
- 6698 Sayılı Kanun Madde 13/2 uyarınca, veri sorumlusu başvuruda yer alan talepleri en kısa sürede ve **en geç otuz (30) gün içinde** sonuçlandırmak zorundadır.
- **Trafik Işığı Renk Kodları (Traffic-Light Countdown):**
  - 🟢 **Yeşil (> 15 gün):** Yasal süre güvenli aralıkta.
  - 🟡 **Sarı (6 - 15 gün):** İnceleme sürecinin hızlandırılması tavsiye edilir.
  - 🔴 **Kırmızı (1 - 5 gün):** 🚨 Yasal süre aşımı riski! Kritik acil durum rozeti.
  - ⬛ **Bordo (<= 0 gün):** 🚨 Yasal süre doldu uyarısı.
- **Yönetici Acil Uyarı Banner'ı:** Son 5 güne giren veya süresi dolan başvurular olduğunda yönetim panelinin en üstünde dikkat çekici uyarı şeridi açılır.

### 2. 📨 KEP (Kayıtlı Elektronik Posta) Doğrulayıcısı & BTK Standartları
- Başvuru sahibinin cevap kanalı olarak KEP seçmesi halinde adresin **BTK standartlarına (`.kep.tr`)** ve yetkili KEPHS sağlayıcılarına (PTT KEP, TNB KEP, TÜRKKEP, E-Tuğra vb.) uygunluğu anlık olarak denetlenir.
- Form doldurulurken anlık doğrulama rozeti çıkar ve geçersiz format girişleri sunucu/istemci tarafında engellenir.

### 3. 🔍 KVKK Md. 11/13 İlgili Kişi Başvuru Durum Sorgulama Portalı (`takip.html` & `/takip`)
- Başvuru sahibine form onayında verilen referans kodu (`KVKK-2026-XXXXXX`) ile çalışan halka açık sade takip arayüzü.
- **Gizlilik Korumalı Maskeleme:** İlgili kişinin ad-soyad bilgileri KVKK ilkelerine uygun olarak maskelenir (`A*** Y***`).
- **Görsel İlerleme Çubuğu & Yasal Sayaç:** 30 günlük yasal yanıtlama sürecinden kaç gün kaldığı dinamik yüzde çubuğu ile gösterilir.
- **Gerekçeli Karar Notu:** Veri sorumlusunun girdiği yasal yanıt özeti ve kararı başvuru sahibi tarafından anında görüntülenebilir.

### 4. 📄 KVKK Md. 13/3 Gerekçeli Karar Belgesi (A4 Yazdırılabilir / PDF Kaydedilebilir)
- 6698 Sayılı Kanun Madde 13/3 uyarınca; veri sorumlusunun talebi kabul veya gerekçesini açıklayarak reddetmesi ve cevabını yazılı veya elektronik ortamda bildirmesi esastır.
- Sistem, sonuçlandırılan her başvuru için tek tıkla resmi şirket antetli, yasal gerekçeli, talep edilen KVKK Md. 11 hakları dökümlü, **KVKK Md. 14 Kişisel Verileri Koruma Kurulu'na Şikayet Hakkı Bildirimini** içeren ve e-imza/kaşe alanları barındıran **A4 formatında standart Gerekçeli Karar Belgesi** üretir.
- Başvuru sahipleri de durum sorgulama sayfasından (`/takip`) resmi karar belgesini tek tıkla yazdırabilir veya PDF olarak indirebilir.

### 5. 📊 VERBİS Yıllık Faaliyet & Uyum Raporu Motoru
- Veri Sorumluları Sicil Bilgi Sistemi (VERBİS) ve KVKK denetimleri için yıllık istatistiki uyum raporu üretir.
- Toplam başvuru sayısı, yasal 30 günlük süreye uyum yüzdesi, ortalama yanıt süresi, hak bazında talep dağılımı ve başvuru sahibi ilişki dağılımı grafiksel KPI kartları ve A4 çıktısı olarak sunulur.

### 6. 📨 KEP Resmi Yanıt Paketi & Excel Uyumlu CSV Dışa Aktarımı
- **KEP Resmi Yanıt Şablonu:** Yetkili KEP sağlayıcıları (PTT KEP, TÜRKKEP vb.) üzerinden gönderilecek resmi cevabın yasal konu başlığı, tebliğ metni ve mevzuat referanslarını otomatik hazırlar.
- **Excel/CSV Export:** UTF-8 BOM destekli Türkçe karakter korumalı dışa aktarım ile tüm başvurular tek tıkla tabloya dönüştürülür.

### 7. 🛡️ Yönetim Paneli (`admin.html`) & SQLite Gerekçeli Karar Kaydı
- Başvuru arama, filtreleme, inceleme, canlı KEP yanıt motoru ve karar belgesi görüntüleme.
- Karar ve durum güncellemesi ("İnceleniyor", "Hukuk Biriminde", "Cevaplandı", "Reddedildi") doğrudan SQLite veritabanında kalıcı olarak saklanır.

---

## 🚀 Hızlı Başlangıç

### Seçenek 1: Windows'ta Tek Tıkla Çalıştırma
Klasördeki **`Baslat.bat`** dosyasına çift tıklayın! Yerel sunucu otomatik başlar:
- **Başvuru Formu:** `http://localhost:8080`
- **Durum Sorgulama:** `http://localhost:8080/takip`
- **Yönetim Paneli:** `http://localhost:8080/admin`

### Seçenek 2: Linux & macOS
```bash
git clone https://github.com/eimza-kep/kurumsal-kvkk-basvuru-scripti.git
cd kurumsal-kvkk-basvuru-scripti
chmod +x baslat.sh
./baslat.sh
```

### Seçenek 3: Docker ile Çalıştırma
```bash
docker build -t kvkk-portal .
docker run -d -p 8080:8080 --name kvkk-app kvkk-portal
```

### Seçenek 4: Paylaşımlı Hosting / cPanel / Plesk (PHP 7.4+ veya 8.x)
1. Dosyaları sunucunuzdaki `public_html/kvkk` dizinine yükleyin.
2. `api.php` otomatik olarak JSON veritabanını (`kvkk_submissions.json`) oluşturacaktır.
3. Tarayıcınızda `https://siteniz.com/kvkk/` adresini açın!

---

## 🍪 Çerez Banner'ını Sitenize Ekleme

KVKK onay barını mevcut web sitenize eklemek için `<body>` etiketinin hemen önüne şu satırı yapıştırmanız yeterlidir:

```html
<script src="https://siteniz.com/kvkk/cookie-banner.js"></script>
```

---

## 📡 REST API Referansı

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/api/submit` | Yeni KVKK ilgili kişi başvurusunu kaydeder ve takip kodu üretir. KEP adresi formatını doğrular. |
| `GET` | `/api/list` | Tüm başvuruları 30 günlük yasal süre sayacı metrikleriyle birlikte listeler. |
| `POST` | `/api/track` | Takip kodu ve kimlik doğrulama ile maskelenmiş kamuya açık başvuru durumunu döner. |
| `POST` | `/api/status` | Veri sorumlusu tarafından başvuru durumunu ve gerekçeli yanıt notunu günceller. |
| `GET` | `/api/karar-belgesi-html?tracking_code=...` | KVKK Md. 13/3 uyumlu resmi gerekçeli karar belgesini A4 HTML formatında sunar. |
| `GET` | `/api/kep-cevap-sablonu?tracking_code=...` | Resmi KEP yanıt paketi, konu ve gövde şablonunu JSON olarak üretir. |
| `GET` | `/api/verbis-raporu-json` | VERBİS uyum raporu metriklerini ve yasal süre istatistiklerini döner. |
| `GET` | `/api/verbis-raporu-html` | Yazdırılabilir A4 formatında VERBİS yıllık faaliyet ve uyum raporunu görüntüler. |
| `GET` | `/api/export-csv` | Excel uyumlu UTF-8 BOM CSV formatında tüm başvuruları indirir. |
| `GET` | `/api/validate-kep?kep=...` | KEP adresinin BTK standartlarına uygunluğunu anlık olarak test eder. |
| `GET` | `/health` | Servis sağlık durum kontrolü. |

---

## 📊 Dosya Mimarisi

```
kurumsal-kvkk-basvuru-scripti/
├── index.html                  # İlgili kişi başvuru formu ve KEP format denetleyicisi
├── takip.html                  # Başvuru durum, 30 günlük yasal sayaç & karar belgesi portalı
├── admin.html                  # Yönetici paneli, yasal süre banner'ı, VERBİS raporu & KEP motoru
├── server.py                   # Bağımsız Python HTTP + SQLite REST sunucusu (Port 8080)
├── api.php                     # Paylaşımlı hosting ve cPanel için PHP REST backend
├── cookie-banner.js            # Bağımsız KVKK çerez onay banner'ı
├── Dockerfile                  # Konteyner kurulum dosyası
├── Baslat.bat                  # Windows tek tıkla başlatıcı
├── baslat.sh                   # Linux / macOS başlatıcı
├── scripts/
│   ├── kvkk_validation_engine.py  # KEP doğrulama, yasal 30 gün sayacı & maskeleme motoru
│   ├── kvkk_decision_generator.py # KVKK Md. 13/3 karar belgesi, VERBİS raporu & KEP şablonu
│   └── test_kvkk.py               # 11/11 kapsamlı birim ve entegrasyon test süiti
├── .github/
│   └── workflows/ci.yml        # Otomatik GitHub Actions CI testi
└── README.md                   # Dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

Tüm doğrulama kurallarını ve SQLite akışlarını test etmek için:

```bash
python scripts/test_kvkk.py
```

---

## 🌐 Veri Gizliliği & E-Dönüşüm Açık Kaynak Ekosistemi

Bu KVKK başvuru ve uyum aracı, [@eimza-kep](https://github.com/eimza-kep) açık kaynak ekosisteminin veri koruma ve regülasyon modülüdür. İlgili diğer araçlar:

* 📨 [kep-adresi-dogrulayici](https://github.com/eimza-kep/kep-adresi-dogrulayici) - KVKK 13. madde uyarınca ilgili kişiye resmi KEP cevabı gönderme ve adres doğrulama.
* 📄 [python-pdf-eimza-dogrulayici](https://github.com/eimza-kep/python-pdf-eimza-dogrulayici) - E-İmzalı dijital açık rıza ve taahhütname belgelerini doğrulama kütüphanesi.
* 👥 [kurumsal-ik-is-basvuru-scripti](https://github.com/eimza-kep/kurumsal-ik-is-basvuru-scripti) - Çalışan adayları için KVKK uyumlu CV ve özgeçmiş toplama portali.
* 🏢 [kurumsal-isg-ziyaretci-kayit-scripti](https://github.com/eimza-kep/kurumsal-isg-ziyaretci-kayit-scripti) - Ziyaretçi ve kamera kaydı aydınlatma metinleri onay portali.
* ⭐ [kobi-musteri-memnuniyet-nps-scripti](https://github.com/eimza-kep/kobi-musteri-memnuniyet-nps-scripti) - KOBİ müşteri deneyimi, NPS analitiği ve Google Haritalar kancası.
* 🌟 [awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum) - Türkiye e-Dönüşüm açık kaynak araçları ve kütüphaneleri kürasyonu.

---

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Kurumsal ve ticari web sitelerinde özgürce kullanılabilir.
