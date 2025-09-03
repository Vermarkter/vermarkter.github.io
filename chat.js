// AI Chat Bot for Marketing in Deutschland
class ChatBot {
  constructor() {
    this.isOpen = false;
    this.responses = {
      de: {
        greeting: "Hallo! 👋 Ich bin Ihr digitaler Marketing-Assistent. Wie kann ich Ihnen helfen?",
        services: "Wir bieten Website-Entwicklung, Google Ads, SEO und Social Media Marketing. Welcher Service interessiert Sie?",
        pricing: "Unsere Preise sind projektabhängig. Kontaktieren Sie uns für ein kostenloses Angebot über Telegram: @Marketing_in_Deutschland",
        contact: "Sie können uns über Telegram erreichen: https://t.me/Marketing_in_Deutschland oder per E-Mail: info@marketing-in-deutschland.de",
        experience: "Wir haben über 8 Jahre Erfahrung im digitalen Marketing und haben bereits 150+ erfolgreiche Projekte abgeschlossen.",
        default: "Entschuldigung, ich verstehe Ihre Frage nicht ganz. Können Sie sie anders formulieren? Oder kontaktieren Sie uns direkt über Telegram für persönliche Beratung."
      },
      en: {
        greeting: "Hello! 👋 I'm your digital marketing assistant. How can I help you?",
        services: "We offer website development, Google Ads, SEO, and social media marketing. Which service interests you?",
        pricing: "Our prices depend on the project. Contact us for a free quote via Telegram: @Marketing_in_Deutschland",
        contact: "You can reach us via Telegram: https://t.me/Marketing_in_Deutschland or email: info@marketing-in-deutschland.de",
        experience: "We have over 8 years of experience in digital marketing and have completed 150+ successful projects.",
        default: "Sorry, I don't quite understand your question. Can you rephrase it? Or contact us directly via Telegram for personal consultation."
      },
      uk: {
        greeting: "Привіт! 👋 Я ваш асистент з цифрового маркетингу. Як я можу вам допомогти?",
        services: "Ми пропонуємо розробку веб-сайтів, Google Ads, SEO та маркетинг в соціальних мережах. Яка послуга вас цікавить?",
        pricing: "Наші ціни залежать від проекту. Зв'яжіться з нами для безкоштовної пропозиції через Telegram: @Marketing_in_Deutschland",
        contact: "Ви можете зв'язатися з нами через Telegram: https://t.me/Marketing_in_Deutschland або email: info@marketing-in-deutschland.de",
        experience: "У нас понад 8 років досвіду в цифровому маркетингу, і ми завершили 150+ успішних проектів.",
        default: "Вибачте, я не зовсім розумію ваше питання. Чи можете ви перефразувати його? Або зв'яжіться з нами безпосередньо через Telegram для особистої консультації."
      },
      ru: {
        greeting: "Привет! 👋 Я ваш помощник по цифровому маркетингу. Как я могу вам помочь?",
        services: "Мы предлагаем разработку веб-сайтов, Google Ads, SEO и маркетинг в социальных сетях. Какая услуга вас интересует?",
        pricing: "Наши цены зависят от проекта. Свяжитесь с нами для бесплатного предложения через Telegram: @Marketing_in_Deutschland",
        contact: "Вы можете связаться с нами через Telegram: https://t.me/Marketing_in_Deutschland или email: info@marketing-in-deutschland.de",
        experience: "У нас более 8 лет опыта в цифровом маркетинге, и мы завершили 150+ успешных проектов.",
        default: "Извините, я не совсем понимаю ваш вопрос. Можете ли вы перефразировать его? Или свяжитесь с нами напрямую через Telegram для личной консультации."
      },
      pl: {
        greeting: "Cześć! 👋 Jestem twoim asystentem marketingu cyfrowego. Jak mogę ci pomóc?",
        services: "Oferujemy tworzenie stron internetowych, Google Ads, SEO i marketing w mediach społecznościowych. Która usługa cię interesuje?",
        pricing: "Nasze ceny zależą od projektu. Skontaktuj się z nami po bezpłatną wycenę przez Telegram: @Marketing_in_Deutschland",
        contact: "Możesz skontaktować się z nami przez Telegram: https://t.me/Marketing_in_Deutschland lub email: info@marketing-in-deutschland.de",
        experience: "Mamy ponad 8 lat doświadczenia w marketingu cyfrowym i ukończyliśmy 150+ udanych projektów.",
        default: "Przepraszam, nie do końca rozumiem twoje pytanie. Czy możesz je przeformułować? Lub skontaktuj się z nami bezpośrednio przez Telegram w celu osobistej konsultacji."
      }
    };
    
    this.keywords = {
      services: ['service', 'услуга', 'послуга', 'usługa', 'leistung', 'website', 'seo', 'ads', 'social'],
      pricing: ['price', 'cost', 'цена', 'ціна', 'cena', 'preis', 'стоимость', 'вартість'],
      contact: ['contact', 'контакт', 'telefon', 'email', 'telegram'],
      experience: ['experience', 'опыт', 'досвід', 'doświadczenie', 'erfahrung']
    };
    
    this.currentLanguage = 'uk';
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
      this.sendBotMessage(this.responses[this.currentLanguage].greeting);
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
    
    // Generate bot response
    setTimeout(() => {
      const botResponse = this.generateResponse(userMessage);
      this.addMessage(chatBody, 'bot', botResponse);
      chatBody.scrollTop = chatBody.scrollHeight;
    }, Math.random() * 1000 + 500); // Random delay between 0.5-1.5 seconds
    
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  addMessage(container, type, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `msg ${type}`;
    messageDiv.innerHTML = `<div class="bubble">${message}</div>`;
    container.appendChild(messageDiv);
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
      
      // Send greeting if it's the first time opening
      if (document.querySelectorAll('#chatBody .msg').length <= 1) {
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