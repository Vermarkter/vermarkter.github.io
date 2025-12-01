(function () {
  // --- ЗМІННІ ---
  const body = document.body;
  const header = document.querySelector('header');
  const themeToggle = document.querySelector('.theme-toggle');
  const mobileToggle = document.querySelector('.mobile-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  const langToggle = document.querySelector('.lang-toggle');
  const langMenu = document.querySelector('.lang-menu');
  
  // Елементи для Hero
  const countdownEl = document.getElementById('countdown-timer') || document.getElementById('countdown');
  const progressFill = document.getElementById('progress-fill');
  const progressValue = document.getElementById('progress-value');
  
  // Елементи Cookie & Chat
  const cookieBanner = document.getElementById('cookie-banner');
  const cookieAccept = document.getElementById('cookie-accept');
  const chatbotToggle = document.getElementById('chatbot-toggle');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotWindow = document.getElementById('chatbot-window');
  const chatbotSend = document.getElementById('chatbot-send');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotBody = document.getElementById('chatbot-body');

  // Елементи Калькулятора (ДОДАНО)
  const budgetInput = document.getElementById('budget');
  const budgetRange = document.getElementById('budget-range');
  const platformSelect = document.getElementById('platform');
  const resImpressions = document.getElementById('impressions');
  const resClicks = document.getElementById('clicks');
  const resLeads = document.getElementById('cpa'); // Тут виводимо ліди або CPA

  // --- 1. ТЕМА ---
  function initTheme() {
    if (!themeToggle) return;
    const stored = localStorage.getItem('theme');
    if (stored === 'light') body.classList.add('theme-light');
    
    themeToggle.addEventListener('click', () => {
      const isLight = body.classList.toggle('theme-light');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
  }

  // --- 2. МОБІЛЬНЕ МЕНЮ ---
  function initMobileMenu() {
    if (!mobileToggle || !mobileMenu) return;
    mobileToggle.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('show');
      mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // --- 3. МОВИ ---
  function initLangSwitcher() {
    if (!langToggle || !langMenu) return;
    langToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      langMenu.classList.toggle('show');
    });
    document.addEventListener('click', (e) => {
      if (!langMenu.contains(e.target) && !langToggle.contains(e.target)) {
        langMenu.classList.remove('show');
      }
    });
  }

  // --- 4. ТАЙМЕР ---
  function initCountdown() {
    if (!countdownEl) return;
    const duration = 24 * 60 * 60 * 1000; // 24 години
    const key = 'ua_countdown_deadline';
    let deadline = localStorage.getItem(key);
    
    if (!deadline || Number(deadline) < Date.now()) {
        deadline = Date.now() + duration;
        localStorage.setItem(key, String(deadline));
    }

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
        countdownEl.textContent = '00:00:00';
        return;
      }
      countdownEl.textContent = format(remaining);
      requestAnimationFrame(tick);
    };
    tick();
  }

  // --- 5. ПРОГРЕС БАР ---
  function initProgress() {
    if (!progressFill) return;
    const target = 82; // 82%
    let current = 0;
    const step = () => {
      current += 1;
      if (current > target) current = target;
      progressFill.style.width = `${current}%`;
      if (progressValue) progressValue.textContent = `${current}%`;
      if (current < target) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  // --- 6. КАЛЬКУЛЯТОР (ДОДАНО) ---
  function initCalculator() {
    if (!budgetInput || !budgetRange || !platformSelect) return;

    function calculate() {
        const budget = parseInt(budgetInput.value) || 0;
        const platform = platformSelect.value;
        
        let cpc = 0.5; // Default
        if (platform === 'meta') cpc = 0.4;
        if (platform === 'tiktok') cpc = 0.2;
        if (platform === 'google') cpc = 0.8;

        const clicks = Math.floor(budget / cpc);
        const impressions = clicks * 25; // Приблизно
        const leads = Math.floor(clicks * 0.05); // 5% конверсія

        // Оновлення значень
        if(resImpressions) resImpressions.textContent = impressions.toLocaleString();
        if(resClicks) resClicks.textContent = clicks.toLocaleString();
        
        // Тут ми використовуємо поле CPA для відображення лідів або ціни
        if(resLeads) resLeads.textContent = leads + " (прогноз)"; 
        
        // Оновлення інших полів якщо вони є (CTR, CPC)
        const elCpc = document.getElementById('cpc');
        if(elCpc) elCpc.textContent = cpc + ' €';
    }

    // Синхронізація
    budgetInput.addEventListener('input', (e) => {
        budgetRange.value = e.target.value;
        calculate();
    });
    budgetRange.addEventListener('input', (e) => {
        budgetInput.value = e.target.value;
        calculate();
    });
    platformSelect.addEventListener('change', calculate);

    // Перший запуск
    calculate();
  }

  // --- 7. COOKIE BANNER ---
  function initCookieBanner() {
    if (!cookieBanner || !cookieAccept) return;
    if (!localStorage.getItem('cookie_consent')) {
      cookieBanner.style.display = 'flex';
    }
    cookieAccept.addEventListener('click', () => {
      localStorage.setItem('cookie_consent', 'true');
      cookieBanner.style.display = 'none';
      // Тут можна запускати Google Analytics
    });
  }

  // --- 8. CHATBOT ---
  function appendMessage(text, type = 'bot') {
    if (!chatbotBody) return;
    const bubble = document.createElement('div');
    bubble.className = `chatbot-message ${type}`;
    bubble.textContent = text;
    chatbotBody.appendChild(bubble);
    chatbotBody.scrollTop = chatbotBody.scrollHeight;
  }

  function initChatbot() {
    if (!chatbotToggle || !chatbotWindow) return;

    chatbotToggle.addEventListener('click', () => {
      chatbotWindow.classList.toggle('show');
      if (chatbotWindow.classList.contains('show') && chatbotBody.children.length === 0) {
          // Привітання при першому відкритті
          appendMessage('Вітаю! Я AI-помічник. Чим можу допомогти?');
      }
    });

    if (chatbotClose) {
        chatbotClose.addEventListener('click', () => chatbotWindow.classList.remove('show'));
    }

    if (chatbotSend && chatbotInput) {
      const sendMessage = () => {
        const val = chatbotInput.value.trim();
        if (!val) return;
        appendMessage(val, 'user');
        chatbotInput.value = '';
        // Імітація відповіді
        setTimeout(() => appendMessage('Дякуємо! Менеджер відповість вам протягом 15 хвилин.'), 1000);
      };

      chatbotSend.addEventListener('click', sendMessage);
      chatbotInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
      });
    }
  }

  // --- ЗАПУСК ВСЬОГО ---
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    initLangSwitcher();
    initCountdown();
    initProgress();
    initCalculator(); // Тепер калькулятор працюватиме!
    initCookieBanner();
    initChatbot();
  });

})();
