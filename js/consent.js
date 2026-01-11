/**
 * VERMARKTER - Cookie Consent Manager
 * GDPR-compliant cookie banner
 */

class ConsentManager {
  constructor() {
    this.cookieBanner = document.getElementById('cookieBanner');
    this.acceptButton = document.getElementById('acceptCookies');
    this.declineButton = document.getElementById('declineCookies');
    this.consentKey = 'vermarkter_cookie_consent';

    this.init();
  }

  init() {
    if (!this.cookieBanner) return;

    // Check if consent already given
    const consent = this.getConsent();

    if (consent === null) {
      // No consent yet - show banner after delay
      setTimeout(() => {
        this.showBanner();
      }, 1500);
    } else if (consent === 'accepted') {
      // Load analytics or tracking scripts here
      this.enableTracking();
    }

    // Event listeners
    if (this.acceptButton) {
      this.acceptButton.addEventListener('click', () => this.accept());
    }

    if (this.declineButton) {
      this.declineButton.addEventListener('click', () => this.decline());
    }
  }

  showBanner() {
    if (this.cookieBanner) {
      this.cookieBanner.classList.add('show');
    }
  }

  hideBanner() {
    if (this.cookieBanner) {
      this.cookieBanner.classList.remove('show');
    }
  }

  accept() {
    this.setConsent('accepted');
    this.hideBanner();
    this.enableTracking();
  }

  decline() {
    this.setConsent('declined');
    this.hideBanner();
  }

  getConsent() {
    return localStorage.getItem(this.consentKey);
  }

  setConsent(value) {
    localStorage.setItem(this.consentKey, value);
  }

  enableTracking() {
    // Only enable tracking if user accepted
    // Example: Load Google Analytics
    // if (typeof gtag !== 'undefined') {
    //   gtag('consent', 'update', {
    //     'analytics_storage': 'granted'
    //   });
    // }

    console.log('Cookie consent accepted - tracking enabled');
  }
}

// Initialize consent manager when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new ConsentManager();
  });
} else {
  new ConsentManager();
}
