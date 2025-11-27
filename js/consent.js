(function() {
  const CONSENT_KEY = 'cookie_consent';
  let analyticsLoaded = false;

  function injectScript(src) {
    return new Promise((resolve, reject) => {
      const existing = document.querySelector(`script[src="${src}"]`);
      if (existing) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.async = true;
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function loadAnalytics() {
    if (analyticsLoaded) return;
    analyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag(){ dataLayer.push(arguments); };

    await injectScript('https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX');
    window.gtag('js', new Date());
    window.gtag('config', 'G-Q707N1FHS1');
  }

  function hideBanner(banner) {
    banner.classList.remove('show');
    banner.setAttribute('aria-hidden', 'true');
  }

  function showBanner(banner) {
    banner.classList.add('show');
    banner.setAttribute('aria-hidden', 'false');
  }

  function handleAccept(banner) {
    localStorage.setItem(CONSENT_KEY, 'true');
    hideBanner(banner);
    loadAnalytics();
  }

  function initConsent() {
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('cookie-accept');
    const settingsBtn = document.getElementById('cookie-settings');
    const settingsInfo = document.getElementById('cookie-settings-info');

    if (!banner || !acceptBtn || !settingsBtn) return;

    const storedConsent = localStorage.getItem(CONSENT_KEY);
    if (storedConsent === 'true') {
      hideBanner(banner);
      loadAnalytics();
      return;
    }

    showBanner(banner);

    acceptBtn.addEventListener('click', () => handleAccept(banner));
    settingsBtn.addEventListener('click', () => {
      if (settingsInfo) settingsInfo.classList.toggle('show');
    });
  }

  document.addEventListener('DOMContentLoaded', initConsent);

  window.loadAnalytics = loadAnalytics;
})();
