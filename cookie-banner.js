/**
 * cookie-banner.js
 * -----------------
 * 6698 Sayılı KVKK ve Kurul İlke Kararlarına Uyumlu Hafif Çerez İzin Barı.
 * Herhangi bir web sitesine 1 satır ile eklenir:
 * <script src="cookie-banner.js"></script>
 */

(function() {
    if (localStorage.getItem('kvkk_cookie_consent')) return;

    const styles = `
        .kvkk-cookie-overlay {
            position: fixed; bottom: 20px; left: 20px; right: 20px; max-width: 520px;
            background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            padding: 20px; z-index: 999999; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b; animation: kvkkSlideUp 0.3s ease-out;
        }
        @keyframes kvkkSlideUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .kvkk-cookie-title { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
        .kvkk-cookie-text { font-size: 0.82rem; color: #475569; line-height: 1.45; margin-bottom: 14px; }
        .kvkk-cookie-text a { color: #1e40af; text-decoration: underline; font-weight: 600; }
        .kvkk-cookie-actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .kvkk-btn {
            padding: 8px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; cursor: pointer;
            border: none; transition: all 0.2s;
        }
        .kvkk-btn-accept { background: #1e40af; color: white; }
        .kvkk-btn-accept:hover { background: #1d4ed8; }
        .kvkk-btn-reject { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }
        .kvkk-btn-reject:hover { background: #e2e8f0; }
    `;

    const styleSheet = document.createElement("style");
    styleSheet.innerText = styles;
    document.head.appendChild(styleSheet);

    const banner = document.createElement("div");
    banner.className = "kvkk-cookie-overlay";
    banner.innerHTML = `
        <div class="kvkk-cookie-title">
            <span>🍪 Çerez ve Gizlilik Tercihleriniz</span>
        </div>
        <div class="kvkk-cookie-text">
            Sitemizde deneyiminizi iyileştirmek, trafiği analiz etmek ve 6698 sayılı KVKK kapsamında temel site fonksiyonlarını sağlamak amacıyla çerezler (cookies) kullanılmaktadır. 
            Detaylı bilgi için <a href="#" onclick="alert('KVKK Çerez Aydınlatma Metni'); return false;">Çerez Aydınlatma Metnimizi</a> inceleyebilirsiniz.
        </div>
        <div class="kvkk-cookie-actions">
            <button class="kvkk-btn kvkk-btn-accept" id="kvkkAcceptAll">Tümünü Kabul Et</button>
            <button class="kvkk-btn kvkk-btn-reject" id="kvkkRejectNonEssential">Yalnızca Zorunlu Çerezler</button>
        </div>
    `;

    document.body.appendChild(banner);

    document.getElementById("kvkkAcceptAll").onclick = function() {
        localStorage.setItem("kvkk_cookie_consent", JSON.stringify({ choice: "all", date: new Date().toISOString() }));
        banner.remove();
    };

    document.getElementById("kvkkRejectNonEssential").onclick = function() {
        localStorage.setItem("kvkk_cookie_consent", JSON.stringify({ choice: "essential", date: new Date().toISOString() }));
        banner.remove();
    };
})();
