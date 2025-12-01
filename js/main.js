(function () {
  const body = document.body;
  const header = document.querySelector('header');
  const themeToggle = document.querySelector('.theme-toggle');
  const mobileToggle = document.querySelector('.mobile-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  const langToggle = document.querySelector('.lang-toggle');
  const langMenu = document.querySelector('.lang-menu');
  const countdownEl = document.getElementById('countdown-timer') || document.getElementById('countdown');
  const progressFill = document.getElementById('progress-fill');
  const progressValue = document.getElementById('progress-value');
  const cookieBanner = document.getElementById('cookie-banner');
  const cookieAccept = document.getElementById('cookie-accept');
  const chatbotToggle = document.getElementById('chatbot-toggle');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotWindow = document.getElementById('chatbot-window');
  const chatbotSend = document.getElementById('chatbot-send');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotBody = document.getElementById('chatbot-body');

  function initTheme() {
    if (!themeToggle) return;
    const stored = localStorage.getItem('theme');
    if (stored === 'light') body.classList.add('theme-light');
    themeToggle.addEventListener('click', () => {
      const isLight = body.classList.toggle('theme-light');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
  }

  function initMobileMenu() {
    if (!mobileToggle || !mobileMenu) return;
    mobileToggle.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('show');
      mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  function initLangSwitcher() {
    if (!langToggle || !langMenu) return;
    langToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      langMenu.classList.toggle('show');
      const expanded = langMenu.classList.contains('show');
      langToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    });
    document.addEventListener('click', (e) => {
      if (!langMenu.contains(e.target) && !langToggle.contains(e.target)) {
        langMenu.classList.remove('show');
        langToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function initCountdown() {
    if (!countdownEl) return;
    const duration = 24 * 60 * 60 * 1000;
    const key = 'ua_countdown_deadline';
    const stored = localStorage.getItem(key);
    const deadline = stored ? Number(stored) : Date.now() + duration;
    if (!stored) localStorage.setItem(key, String(deadline));

    const format = (ms) => {
      const total = Math.max(0, Math.floor(ms / 1000));
      const h = String(Math.floor(total / 3600)).padStart(2, '0');
      const m = String(Math.floor((total % 3600) / 60)).padStart(2, '0');
      const s = String(total % 60).padStart(2, '0');
      return `${h}:${m}:${s}`;
    };

    const tick = () => {
      const remaining = deadline - Date.now();
      if (remaining <= 0) {
        countdownEl.textContent = 'Акція завершена';
        countdownEl.classList.add('expired');
        return;
      }
      countdownEl.textContent = format(remaining);
      requestAnimationFrame(tick);
    };

    tick();
  }

  function initProgress() {
    if (!progressFill) return;
    const target = 82;
    let current = 0;
    const step = () => {
      current += 1;
      if (current > target) current = target;
      progressFill.style.width = `${current}%`;
      if (progressValue) progressValue.textContent = `${current}%`;
      progressFill.parentElement?.setAttribute('aria-valuenow', String(current));
      if (current < target) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function ensureMarqueeClones() {
    const marquees = document.querySelectorAll('.marquee');
    marquees.forEach((marquee) => {
      const track = marquee.querySelector('.marquee-track');
      if (!track) return;
      const hasClone = marquee.querySelectorAll('.marquee-track').length > 1;
      if (!hasClone) {
        const clone = track.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        marquee.appendChild(clone);
      }
    });
  }

  function initCookieBanner() {
    if (!cookieBanner || !cookieAccept) return;
    const key = 'cookie_consent';
    const consent = localStorage.getItem(key);
    if (consent === 'true') {
      cookieBanner.style.display = 'none';
    } else {
      cookieBanner.style.display = 'flex';
    }
    cookieAccept.addEventListener('click', () => {
      localStorage.setItem(key, 'true');
      cookieBanner.style.display = 'none';
    });
  }

  function appendMessage(text, type = 'bot') {
    if (!chatbotBody) return;
    const bubble = document.createElement('div');
    bubble.className = `message ${type}`;
    bubble.textContent = text;
    chatbotBody.appendChild(bubble);
    chatbotBody.scrollTop = chatbotBody.scrollHeight;
  }

  function initChatbot() {
    if (!chatbotToggle || !chatbotWindow) return;
    const close = () => chatbotWindow.classList.remove('show');
    chatbotToggle.addEventListener('click', () => {
      const open = chatbotWindow.classList.toggle('show');
      if (open) appendMessage('Вітаю! Я AI-помічник Vermarkter. Чим можемо допомогти?');
    });
    if (chatbotClose) chatbotClose.addEventListener('click', close);
    if (chatbotSend && chatbotInput) {
      chatbotSend.addEventListener('click', () => {
        const val = chatbotInput.value.trim();
        if (!val) return;
        appendMessage(val, 'user');
        chatbotInput.value = '';
        setTimeout(() => appendMessage('Дякуємо! Ми зв’яжемося з вами найближчим часом.'), 400);
      });
      chatbotInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          chatbotSend.click();
        }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    initLangSwitcher();
    initCountdown();
    initProgress();
    ensureMarqueeClones();
    initCookieBanner();
    initChatbot();
  });
})();
