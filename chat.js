// AI Chat Bot for Marketing in Deutschland - Enhanced Multilingual Version
class ChatBot {
  constructor() {
    this.isOpen = false;
    this.currentLanguage = 'ua';
    this.responses = {
      de: {
        greeting: "Hallo! 👋 Ich bin Ihr digitaler Marketing-Assistent. Wie kann ich Ihnen helfen?",
        services: "Wir bieten Website-Entwicklung, Google Ads, SEO und Social Media Marketing. Welcher Service interessiert Sie am meisten?",
        pricing: "Unsere Preise sind projektabhängig und sehr wettbewerbsfähig. Kontaktieren Sie uns für ein kostenloses Angebot über Telegram: @Marketing_in_Deutschland",
        contact: "Sie können uns jederzeit erreichen:\n📱 Telegram: https://t.me/Marketing_in_Deutschland\n📧 E-Mail: info@marketing-in-deutschland.de\n⏰ Wir antworten innerhalb von 2 Stunden!",
        experience: "Wir haben über 8 Jahre Erfahrung im digitalen Marketing und haben bereits 150+ erfolgreiche Projekte abgeschlossen. Unsere Kundenzufriedenheit liegt bei 95%!",
        website: "Wir entwickeln moderne, responsive Websites mit optimaler Performance. Durchschnittliche Ladezeit unter 2 Sekunden garantiert!",
        seo: "Unser SEO-Service erhöht Ihre organische Sichtbarkeit. Durchschnittlich 250% Traffic-Steigerung in 6 Monaten!",
        ads: "Google Ads Management mit messbaren Ergebnissen. ROI-Verbesserung um durchschnittlich 300%!",
        social: "Social Media Marketing für mehr Engagement und Kundenbindung. Follower-Wachstum um 400% möglich!",
        default: "Das ist eine interessante Frage! Für eine detaillierte Beratung kontaktieren Sie uns gerne direkt über Telegram: @Marketing_in_Deutschland"
      },
      en: {
        greeting: "Hello! 👋 I'm your digital marketing assistant. How can I help you today?",
        services: "We offer website development, Google Ads, SEO, and social media marketing. Which service interests you most?",
        pricing: "Our prices are project-dependent and very competitive. Contact us for a free quote via Telegram: @Marketing_in_Deutschland",
        contact: "You can reach us anytime:\n📱 Telegram: https://t.me/Marketing_in_Deutschland\n📧 Email: info@marketing-in-deutschland.de\n⏰ We respond within 2 hours!",
        experience: "We have over 8 years of experience in digital marketing and have completed 150+ successful projects. Our customer satisfaction rate is 95%!",
        website: "We develop modern, responsive websites with optimal performance. Average loading time under 2 seconds guaranteed!",
        seo: "Our SEO service increases your organic visibility. Average 250% traffic increase in 6 months!",
        ads: "Google Ads management with measurable results. ROI improvement by an average of 300%!",
        social: "Social media marketing for more engagement and customer loyalty. Follower growth of 400% possible!",
        default: "That's an interesting question! For detailed consultation, please contact us directly via Telegram: @Marketing_in_Deutschland"
      },
      ua: {
        greeting: "Привіт! 👋 Я ваш асистент з цифрового маркетингу. Як я можу вам допомогти?",
        services: "Ми пропонуємо розробку веб-сайтів, Google Ads, SEO та маркетинг в соціальних мережах. Яка послуга вас найбільше цікавить?",
        pricing: "Наші ціни залежать від проекту та дуже конкурентоспроможні. Зв'яжіться з нами для безкоштовної пропозиції через Telegram: @Marketing_in_Deutschland",
        contact: "Ви можете зв'язатися з нами будь-коли:\n📱 Telegram: https://t.me/Marketing_in_Deutschland\n📧 Email: info@marketing-in-deutschland.de\n⏰ Відповідаємо протягом 2 годин!",
        experience: "У нас понад 8 років досвіду в цифровому маркетингу, і ми завершили 150+ успішних проектів. Наша задоволеність клієнтів становить 95%!",
        website: "Ми розробляємо сучасні, адаптивні веб-сайти з оптимальною продуктивністю. Гарантуємо час завантаження менше 2 секунд!",
        seo: "Наш SEO-сервіс підвищує вашу органічну видимість. В середньому збільшення трафіку на 250% за 6 місяців!",
        ads: "Управління Google Ads з вимірюваними результатами. Покращення ROI в середньому на 300%!",
        social: "Маркетинг в соціальних мережах для більшого залучення та лояльності клієнтів. Можливе зростання підписників на 400%!",
        default: "Це цікаве питання! Для детальної консультації зв'яжіться з нами безпосередньо через Telegram: @Marketing_in_Deutschland"
      },
      ru: {
        greeting: "Привет! 👋 Я ваш помощник по цифровому маркетингу. Как я могу вам помочь?",
        services: "Мы предлагаем разработку веб-сайтов, Google Ads, SEO и маркетинг в социальных сетях. Какая услуга вас больше всего интересует?",
        pricing: "Наши цены зависят от проекта и очень конкурентоспособны. Свяжитесь с нами для бесплатного предложения через Telegram: @Marketing_in_Deutschland",
        contact: "Вы можете связаться с нами в любое время:\n📱 Telegram: https://t.me/Marketing_in_Deutschland\n📧 Email: info@marketing-in-deutschland.de\n⏰ Отвечаем в течение 2 часов!",
        experience: "У нас более 8 лет опыта в цифровом маркетинге, и мы завершили 150+ успешных проектов. Наша удовлетворенность клиентов составляет 95%!",
        website: "Мы разрабатываем современные, адаптивные веб-сайты с оптимальной производительностью. Гарантируем время загрузки менее 2 секунд!",
        seo: "Наш SEO-сервис повышает вашу органическую видимость. В среднем увеличение трафика на 250% за 6 месяцев!",
        ads: "Управление Google Ads с измеримыми результатами. Улучшение ROI в среднем на 300%!",
        social: "Маркетинг в социальных сетях для большего вовлечения и лояльности клиентов. Возможен рост подписчиков на 400%!",
        default: "Это интересный вопрос! Для подробной консультации свяжитесь с нами напрямую через Telegram: @Marketing_in_Deutschland"
      },
      pl: {
        greeting: "Cześć! 👋 Jestem twoim asystentem marketingu cyfrowego. Jak mogę ci pomóc?",
        services: "Oferujemy tworzenie stron internetowych, Google Ads, SEO i marketing w mediach społecznościowych. Która usługa cię najbardziej interesuje?",
        pricing: "Nasze ceny zależą od projektu i są bardzo konkurencyjne. Skontaktuj się z nami po bezpłatną wycenę przez Telegram: @Marketing_in_Deutschland",
        contact: "Możesz skontaktować się z nami w dowolnym momencie:\n📱 Telegram: https://t.me/Marketing_in_Deutschland\n📧 Email: info@marketing-in-deutschland.de\n⏰ Odpowiadamy w ciągu 2 godzin!",
        experience: "Mamy ponad 8 lat doświadczenia w marketingu cyfrowym i ukończyliśmy 150+ udanych projektów. Nasze zadowolenie klientów wynosi 95%!",
        website: "Tworzymy nowoczesne, responsywne strony internetowe o optymalnej wydajności. Gwarantujemy czas ładowania poniżej 2 sekund!",
        seo: "Nasza usługa SEO zwiększa twoją organiczną widoczność. Średnio 250% wzrost ruchu w ciągu 6 miesięcy!",
        ads: "Zarządzanie Google Ads z mierzalnymi rezultatami. Poprawa ROI średnio o 300%!",
        social: "Marketing w mediach społecznościowych dla większego zaangażowania i lojalności klientów. Możliwy wzrost obserwujących o 400%!",
        default: "To ciekawe pytanie! W celu szczegółowej konsultacji skontaktuj się z nami bezpośrednio przez Telegram: @Marketing_in_Deutschland"
      }
    };
    
    this.keywords = {
      services: ['service', 'услуга', 'послуга', 'usługa', 'leistung', 'website', 'seo', 'ads', 'social', 'послуги', 'услуги', 'usługi'],
      pricing: ['price', 'cost', 'цена', 'ціна', 'cena', 'preis', 'стоимость', 'вартість', 'koszt', 'сколько', 'скільки'],
      contact: ['contact', 'контакт', 'telefon', 'email', 'telegram', 'связаться', 'зв\'язатися', 'skontaktować'],
      experience: ['experience', 'опыт', 'досвід', 'doświadczenie', 'erfahrung', 'років', 'лет', 'lat'],
      website: ['website', 'сайт', 'веб-сайт', 'strona', 'webseite', 'site', 'web'],
      seo: ['seo', 'поисковая', 'пошукова', 'оптимизация', 'оптимізація', 'optymalizacja', 'search'],
      ads: ['ads', 'реклама', 'advertising', 'google', 'контекстная', 'контекстна', 'reklama'],
      social: ['social', 'социальные', 'соціальні', 'społeczne', 'facebook', 'instagram', 'smm']
    };
    
    this.init();
  }

  init() {
    this.bindEvents();
    this.updateLanguage();
  }

  bindEvents() {
    // Language change detection
    document.addEventListener('languageChanged', (e) => {
      this.currentLanguage = e.detail.language;
      // Clear chat and send new greeting
      const chatBody = document.getElementById('chatBody');
      if (chatBody) {
        chatBody.innerHTML = '';
        setTimeout(() => {
          this.sendBotMessage(this.responses[this.currentLanguage].greeting);
        }, 300);
      }
    });
  }

  updateLanguage() {
    const langSelect = document.querySelector('#lang');
    if (langSelect) {
      this.currentLanguage = langSelect.value;
    }
  }

  analyzeMessage(message) {
    const lowerMessage = message.toLowerCase();
    
    for (const [category, keywords] of Object.entries(this.keywords)) {
      if (keywords.some(keyword => lowerMessage.includes(keyword))) {
        return category;
      }
    }
    
    return 'default';
  }

  generateResponse(message) {
    const category = this.analyzeMessage(message);
    const responses = this.responses[this.currentLanguage];
    
    return responses[category] || responses.default;
  }

  sendMessage(userMessage) {
    if (!userMessage.trim()) return;

    const chatBody = document.getElementById('chatBody');
    
    // Add user message
    this.addMessage(chatBody, 'user', userMessage);
    
    // Generate bot response with realistic delay
    setTimeout(() => {
      const botResponse = this.generateResponse(userMessage);
      this.addMessage(chatBody, 'bot', botResponse);
      chatBody.scrollTop = chatBody.scrollHeight;
    }, Math.random() * 1500 + 800); // Random delay between 0.8-2.3 seconds
    
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  addMessage(container, type, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `msg ${type}`;
    
    // Handle line breaks in bot messages
    const formattedMessage = message.replace(/\n/g, '<br>');
    messageDiv.innerHTML = `<div class="bubble">${formattedMessage}</div>`;
    
    container.appendChild(messageDiv);
    
    // Add animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    setTimeout(() => {
      messageDiv.style.transition = 'all 0.3s ease';
      messageDiv.style.opacity = '1';
      messageDiv.style.transform = 'translateY(0)';
    }, 50);
  }

  sendBotMessage(message) {
    const chatBody = document.getElementById('chatBody');
    this.addMessage(chatBody, 'bot', message);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  toggle() {
    const panel = document.getElementById('chatPanel');
    const backdrop = document.getElementById('chatBackdrop');
    
    this.isOpen = !this.isOpen;
    
    if (this.isOpen) {
      panel.classList.add('open');
      backdrop.classList.add('open');
      
      // Send greeting if it's the first time opening or chat is empty
      const chatBody = document.getElementById('chatBody');
      if (!chatBody || chatBody.children.length === 0) {
        setTimeout(() => {
          this.sendBotMessage(this.responses[this.currentLanguage].greeting);
        }, 300);
      }
    } else {
      panel.classList.remove('open');
      backdrop.classList.remove('open');
    }
  }
}

// Initialize chat bot
const chatBot = new ChatBot();

// Global functions for HTML onclick handlers
function toggleChat() {
  chatBot.toggle();
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  
  if (message) {
    chatBot.sendMessage(message);
    input.value = '';
  }
}

function handleEnter(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
}

// Export for use in main script
if (typeof window !== 'undefined') {
  window.chatBot = chatBot;
}