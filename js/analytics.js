(function() {
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
    window.gtag('config', 'G-XXXXXXXXXX');
  }

  window.loadAnalytics = loadAnalytics;
})();
