/*!
 * VERMARKTER — Cookie Consent Manager v2
 * GDPR-compliant: 3 choices (Accept All / Analytics Only / Settings)
 * Analytics enabled for both 'accepted' and 'analytics' consent levels
 */

/* ── Тексти для 6 мов ── */
var CONSENT_I18N = {
  de: {
    text:      'Wir verwenden Cookies, um die Website-Leistung zu verbessern und Analysen durchzuführen.',
    acceptAll: 'Alle akzeptieren',
    analytics: 'Nur Analyse',
    settings:  'Einstellungen'
  },
  en: {
    text:      'We use cookies to improve website performance and conduct analytics.',
    acceptAll: 'Accept All',
    analytics: 'Analytics Only',
    settings:  'Settings'
  },
  pl: {
    text:      'Używamy plików cookie, aby poprawić wydajność strony i przeprowadzać analizy.',
    acceptAll: 'Akceptuj wszystkie',
    analytics: 'Tylko analityka',
    settings:  'Ustawienia'
  },
  ru: {
    text:      'Мы используем файлы cookie для улучшения работы сайта и аналитики.',
    acceptAll: 'Принять все',
    analytics: 'Только аналитика',
    settings:  'Настройки'
  },
  tr: {
    text:      'Web sitesi performansını iyileştirmek ve analiz yapmak için çerezler kullanıyoruz.',
    acceptAll: 'Tümünü kabul et',
    analytics: 'Yalnızca analitik',
    settings:  'Ayarlar'
  },
  ua: {
    text:      'Ми використовуємо файли cookie для покращення роботи сайту та аналітики.',
    acceptAll: 'Прийняти все',
    analytics: 'Тільки аналітика',
    settings:  'Налаштування'
  }
};

/* ── Визначення мови ── */
function detectConsentLang() {
  var html = document.documentElement.lang || '';
  var lang = html.substring(0, 2).toLowerCase();
  if (lang === 'uk') lang = 'ua';
  return CONSENT_I18N[lang] ? lang : 'de';
}

/* ══════════════════════════════════════════
   ConsentManager
══════════════════════════════════════════ */
class ConsentManager {
  constructor() {
    this.banner     = document.getElementById('cookieBanner');
    this.consentKey = 'vermarkter_cookie_consent';
    this.lang       = detectConsentLang();
    this.i18n       = CONSENT_I18N[this.lang];

    this.init();
  }

  init() {
    if (!this.banner) return;

    /* Перебудовуємо вміст банера під 3-кнопкову схему */
    this.buildBanner();

    const consent = this.getConsent();

    if (consent === null) {
      setTimeout(() => this.showBanner(), 1500);
    } else if (consent === 'accepted' || consent === 'analytics') {
      this.enableTracking();
    }
  }

  /* ── Будуємо HTML банера ── */
  buildBanner() {
    this.banner.innerHTML = `
      <div class="container">
        <div class="cookie-content">
          <p class="cookie-text">${this.i18n.text}</p>
          <div class="cookie-actions">
            <button class="cookie-btn cookie-btn--primary" id="cookieAcceptAll">
              ${this.i18n.acceptAll}
            </button>
            <button class="cookie-btn cookie-btn--secondary" id="cookieAnalytics">
              ${this.i18n.analytics}
            </button>
            <button class="cookie-btn cookie-btn--link" id="cookieSettings">
              ${this.i18n.settings}
            </button>
          </div>
        </div>
      </div>

      <!-- Settings panel (hidden by default) -->
      <div class="cookie-settings" id="cookieSettingsPanel" style="display:none;">
        <div class="container">
          <div class="cookie-settings__grid">
            <label class="cookie-toggle">
              <input type="checkbox" checked disabled>
              <span class="cookie-toggle__label">Necessary <span class="cookie-toggle__badge">Always ON</span></span>
            </label>
            <label class="cookie-toggle">
              <input type="checkbox" id="toggleAnalytics" checked>
              <span class="cookie-toggle__label">Analytics (Google Analytics 4)</span>
            </label>
            <label class="cookie-toggle">
              <input type="checkbox" id="toggleMarketing" checked>
              <span class="cookie-toggle__label">Marketing</span>
            </label>
          </div>
          <button class="cookie-btn cookie-btn--primary" id="cookieSaveSettings" style="margin-top:1rem;">
            ${this.i18n.acceptAll}
          </button>
        </div>
      </div>
    `;

    document.getElementById('cookieAcceptAll').addEventListener('click', () => this.acceptAll());
    document.getElementById('cookieAnalytics').addEventListener('click', () => this.acceptAnalytics());
    document.getElementById('cookieSettings').addEventListener('click', () => this.toggleSettings());
    document.getElementById('cookieSaveSettings').addEventListener('click', () => this.saveSettings());
  }

  showBanner() { this.banner.classList.add('show'); }
  hideBanner()  { this.banner.classList.remove('show'); }

  toggleSettings() {
    var panel = document.getElementById('cookieSettingsPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
  }

  /* ── Варіант А: Прийняти все ── */
  acceptAll() {
    this.setConsent('accepted');
    this.hideBanner();
    this.enableTracking();
  }

  /* ── Варіант Б: Тільки аналітика ── */
  acceptAnalytics() {
    this.setConsent('analytics');
    this.hideBanner();
    this.enableTracking();
  }

  /* ── Варіант В: Зберегти налаштування ── */
  saveSettings() {
    var analytics = document.getElementById('toggleAnalytics')?.checked;
    var marketing = document.getElementById('toggleMarketing')?.checked;

    if (analytics || marketing) {
      this.setConsent(marketing ? 'accepted' : 'analytics');
      this.enableTracking();
    } else {
      this.setConsent('declined');
    }
    this.hideBanner();
  }

  getConsent()        { return localStorage.getItem(this.consentKey); }
  setConsent(value)   { localStorage.setItem(this.consentKey, value); }

  /* ── Вмикає GA4 (викликається для 'accepted' та 'analytics') ── */
  enableTracking() {
    if (window.vermarkterAnalytics && typeof window.vermarkterAnalytics.enable === 'function') {
      window.vermarkterAnalytics.enable();
    }
  }
}

/* ── Старт ── */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new ConsentManager());
} else {
  new ConsentManager();
}
