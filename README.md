# 🛡️ 6698 KVKK İlgili Kişi Başvuru Scripti & Çerez Yönetimi

[![CI](https://github.com/eimza-kep/kurumsal-kvkk-basvuru-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/kurumsal-kvkk-basvuru-scripti/actions/workflows/ci.yml)
[![Canlı Demo](https://img.shields.io/badge/Demo-Canl%C4%B1%20Test%20Et-brightgreen.svg)](https://eimza-kep.github.io/kurumsal-kvkk-basvuru-scripti/)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Kurulum Süresi](https://img.shields.io/badge/Kurulum-1%20Dakika-brightgreen)](#)
[![Bağımlılık](https://img.shields.io/badge/ba%C4%9F%C4%B1ml%C4%B1l%C4%B1k-0%20(S%C4%B1f%C4%B1r)-blue)](#)

Türkiye'de faaliyet gösteren şirketler, e-ticaret siteleri, avukatlar, mali müşavirler ve KOBİ'lerin web sitelerine **1 dakikada kurup çalıştırabileceği**, 6698 sayılı Kişisel Verilerin Korunması Kanunu'na tam uyumlu **İlgili Kişi (Veri Sahibi) Başvuru Formu, Admin Paneli ve Çerez İzin Barı scripti**.

---

## 🌟 Temel Özellikler

1. **Kanuni Standartlara Tam Uyum (KVKK Md. 11 & Md. 13):**
   - Başvuru sahibinin kimlik doğrulama verileri (TCKN, İsim, İletişim, Şirketle İlişki).
   - Kanunun 11. maddesindeki 7 temel hak grubu hazır kontrol kutucukları halinde sunulur.
   - Kanuni 30 günlük yasal yanıt süresi otomatik hesaplanır ve başvuru sahibine bildirilir.
2. **Benzersiz Takip Kodu (Örn: `KVKK-2026-894123`):**
   - Her başvuruya özel takip numarası üretilir; başvuru sahibi formun çıktısını PDF olarak alabilir.
3. **Yönetim Paneli (`admin.html`):**
   - Gelen başvuruları listeleme, arama ve filtreleme.
   - Yasal 30 günlük süre geri sayımı (Son 7 güne giren başvurularda 🚨 kırmızı alarm bildirimi).
   - Başvuruları tek tıkla Excel/CSV formatında dışa aktarma.
4. **Hafif Çerez İzin Barı (`cookie-banner.js`):**
   - Sitenizin `<head>` veya `<body>` etiketine tek satır ekleyerek KVKK uyumlu çerez rıza banner'ını devreye alabilirsiniz.
5. **Çift Arka Uç Desteği (Python & PHP):**
   - **cPanel / Paylaşımlı Hosting:** Doğrudan `api.php` üzerinden JSON depolama ile çalışır (PHP 7.4+ veya 8+).
   - **Kendi Sunucunuz / VPS / Yerel:** Sıfır paket kurulumu gerektiren `server.py` ve dahili SQLite veritabanı.
   - **Statik / Jamstack:** Arka uç olmadan doğrudan `localStorage` ile de çalışabilir!

---

## 🚀 1 Dakikada Kurulum

### Seçenek 1: Windows'ta Tek Tıkla Çalıştırma (Yerel Test)
Klasördeki **`Baslat.bat`** dosyasına çift tıklayın! Yerel sunucu otomatik başlar ve tarayıcınızda form açılır.

### Seçenek 2: Paylaşımlı Hosting / cPanel (Apache & PHP)
1. Bu depodaki dosyaları zip olarak indirin.
2. Sitenizin `public_html/kvkk` (veya dilediğiniz bir klasör) dizinine yükleyin.
3. Tarayıcınızda `https://siteniz.com/kvkk/` adresini açın! Hepsi bu kadar.

### Seçenek 3: Python ile Çalıştırma
```bash
python server.py
```
- Başvuru Formu: `http://localhost:8080/index.html`
- Yönetici Paneli: `http://localhost:8080/admin.html`

---

## 🍪 Çerez Banner'ını Kendi Sitenize Ekleme

Mevcut sitenizin sayfalarına KVKK onay barını eklemek için sayfanızın en altına şu satırı yapıştırmanız yeterlidir:

```html
<script src="https://siteniz.com/kvkk/cookie-banner.js"></script>
```

---

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Kurumsal ve ticari web sitelerinde özgürce kullanılabilir.
