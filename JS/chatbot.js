/**
 * VERMARKTER - Smart Chatbot
 * Text-based assistant that acts as agency employee
 * Helps users understand services and guides to contact
 * Multi-language support: UA, DE, EN, PL, RU, TR
 */

class VermarkterChatbot {
  constructor() {
    this.chatbotButton = document.getElementById('chatbotButton');
    this.isOpen = false;
    this.messages = [];
    this.chatWidget = null;
    this.lang = this.detectLanguage();

    this.init();
  }

  detectLanguage() {
    // Detect language from HTML lang attribute or URL path
    const htmlLang = document.documentElement.lang;
    if (htmlLang) return htmlLang;

    const path = window.location.pathname;
    if (path.includes('/ua/')) return 'uk';
    if (path.includes('/de/')) return 'de';
    if (path.includes('/en/')) return 'en';
    if (path.includes('/pl/')) return 'pl';
    if (path.includes('/ru/')) return 'ru';
    if (path.includes('/tr/')) return 'tr';

    return 'de'; // default
  }

  getTranslation(key) {
    const translations = {
      uk: {
        title: 'Vermarkter Асистент',
        subtitle: 'Як я можу вам допомогти?',
        placeholder: 'Напишіть ваше питання...',
        initialMessage: 'Привіт! Я ваш персональний маркетинговий асистент. Як я можу вам допомогти сьогодні?',
        googleBtn: '🔍 Google Ads',
        metaBtn: '📱 Meta Ads',
        calculatorBtn: '📊 Калькулятор',
        contactBtn: '💬 Контакт',
        tooltip: 'Питання? Я допоможу!',
        hint: '💬 Потрібна допомога? Запитайте мене!',
        googleUser: 'Мене цікавить Google Ads',
        googleBot1: 'Чудово! Google Ads ідеально підходить для гарячих лідів з пошуку. З Performance Max ми охопимо вашу аудиторію по всьому ЄС.',
        googleBot2: 'Бажаєте спочатку протестувати наш ROI-калькулятор, щоб побачити, скільки ви можете заробити з Google Ads?',
        metaUser: 'Мене цікавить Meta Ads',
        metaBot1: 'Відмінно! Facebook & Instagram ідеальні для лідогенерації та E-Commerce. Ми використовуємо ремаркетинг та Lookalike-аудиторії для максимальних конверсій.',
        metaBot2: 'Показати вам, як Meta Ads працює для вашого бізнесу?',
        calculatorUser: 'Покажи калькулятор',
        calculatorBot: 'ROI-калькулятор показує вам реальні прогнози на основі справжніх формул медіапланування. Ви можете тестувати різні сценарії.',
        contactUser: 'Я хочу зв\'язатися',
        contactBot1: 'Дуже раді! Ви можете зв\'язатися з нами напряму:',
        contactBot2: '📧 Email: maps.werbung@gmail.com',
        contactBot3: '💬 Telegram: @Asystentmijbot',
        contactBot4: 'Або заповніть контактну форму, і ми зв\'яжемося з вами протягом 24 годин.',
        priceBot1: 'Наші ціни прозорі та залежать від обсягу проєкту. Використовуйте наш ROI-калькулятор, щоб побачити, які результати можливі з вашим бюджетом.',
        priceBot2: 'Бажаєте персональну консультацію? Я можу зв\'язати вас з нашою командою.',
        helpBot1: 'Я з радістю допоможу! Я можу надати інформацію про:',
        helpBot2: '• Google Ads & Meta Ads кампанії\n• ROI-розрахунок\n• Наші послуги\n• Контактні дані',
        defaultBot1: 'Дякуємо за ваше повідомлення! Наші спеціалізації - Google Ads, Meta Ads та Performance-маркетинг.',
        defaultBot2: 'Для детальних питань рекомендую прямий контакт з нашою командою:',
        defaultBot3: '📧 maps.werbung@gmail.com або 💬 @Asystentmijbot'
      },
      de: {
        title: 'Vermarkter Assistant',
        subtitle: 'Wie kann ich Ihnen helfen?',
        placeholder: 'Schreiben Sie Ihre Frage...',
        initialMessage: 'Hallo! Ich bin Ihr persönlicher Marketing-Assistent. Wie kann ich Ihnen heute helfen?',
        googleBtn: '🔍 Google Ads',
        metaBtn: '📱 Meta Ads',
        calculatorBtn: '📊 Kalkulator',
        contactBtn: '💬 Kontakt',
        tooltip: 'Fragen? Ich helfe Ihnen!',
        hint: '💬 Brauchen Sie Hilfe? Fragen Sie mich!',
        googleUser: 'Ich interessiere mich für Google Ads',
        googleBot1: 'Großartig! Google Ads ist perfekt für heiße Leads aus der Suche. Mit Performance Max erreichen wir Ihre Zielgruppe in der gesamten EU.',
        googleBot2: 'Möchten Sie zuerst unseren ROI-Rechner testen, um zu sehen, wie viel Sie mit Google Ads verdienen können?',
        metaUser: 'Ich interessiere mich für Meta Ads',
        metaBot1: 'Perfekt! Facebook & Instagram sind ideal für Leadgenerierung und E-Commerce. Wir nutzen Remarketing und Lookalike-Audiences für maximale Conversions.',
        metaBot2: 'Soll ich Ihnen zeigen, wie Meta Ads für Ihr Business funktioniert?',
        calculatorUser: 'Zeig mir den Kalkulator',
        calculatorBot: 'Der ROI-Rechner zeigt Ihnen reale Prognosen basierend auf echten Mediaplanung-Formeln. Sie können verschiedene Szenarien testen.',
        contactUser: 'Ich möchte Kontakt aufnehmen',
        contactBot1: 'Sehr gerne! Sie können uns direkt erreichen über:',
        contactBot2: '📧 Email: maps.werbung@gmail.com',
        contactBot3: '💬 Telegram: @Asystentmijbot',
        contactBot4: 'Oder füllen Sie das Kontaktformular aus, und wir melden uns innerhalb von 24 Stunden.',
        priceBot1: 'Unsere Preise sind transparent und variieren je nach Projektumfang. Nutzen Sie unseren ROI-Rechner, um zu sehen, welche Ergebnisse mit Ihrem Budget möglich sind.',
        priceBot2: 'Möchten Sie eine persönliche Beratung? Ich kann Sie mit unserem Team verbinden.',
        helpBot1: 'Ich helfe Ihnen gerne! Ich kann Ihnen Informationen geben zu:',
        helpBot2: '• Google Ads & Meta Ads Kampagnen\n• ROI-Berechnung\n• Unsere Services\n• Kontaktmöglichkeiten',
        defaultBot1: 'Danke für Ihre Nachricht! Unsere Spezialgebiete sind Google Ads, Meta Ads und Performance-Marketing.',
        defaultBot2: 'Für detaillierte Fragen empfehle ich einen direkten Kontakt mit unserem Team:',
        defaultBot3: '📧 maps.werbung@gmail.com oder 💬 @Asystentmijbot'
      },
      en: {
        title: 'Vermarkter Assistant',
        subtitle: 'How can I help you?',
        placeholder: 'Type your question...',
        initialMessage: 'Hello! I\'m your personal marketing assistant. How can I help you today?',
        googleBtn: '🔍 Google Ads',
        metaBtn: '📱 Meta Ads',
        calculatorBtn: '📊 Calculator',
        contactBtn: '💬 Contact',
        tooltip: 'Questions? I can help!',
        hint: '💬 Need help? Ask me!',
        googleUser: 'I\'m interested in Google Ads',
        googleBot1: 'Great! Google Ads is perfect for hot leads from search. With Performance Max we reach your target audience across the EU.',
        googleBot2: 'Would you like to test our ROI calculator first to see how much you can earn with Google Ads?',
        metaUser: 'I\'m interested in Meta Ads',
        metaBot1: 'Perfect! Facebook & Instagram are ideal for lead generation and E-Commerce. We use remarketing and Lookalike Audiences for maximum conversions.',
        metaBot2: 'Shall I show you how Meta Ads works for your business?',
        calculatorUser: 'Show me the calculator',
        calculatorBot: 'The ROI calculator shows you real forecasts based on actual media planning formulas. You can test different scenarios.',
        contactUser: 'I want to get in touch',
        contactBot1: 'Gladly! You can reach us directly via:',
        contactBot2: '📧 Email: maps.werbung@gmail.com',
        contactBot3: '💬 Telegram: @Asystentmijbot',
        contactBot4: 'Or fill out the contact form and we\'ll get back to you within 24 hours.',
        priceBot1: 'Our prices are transparent and vary depending on project scope. Use our ROI calculator to see what results are possible with your budget.',
        priceBot2: 'Would you like a personal consultation? I can connect you with our team.',
        helpBot1: 'I\'m happy to help! I can provide information about:',
        helpBot2: '• Google Ads & Meta Ads campaigns\n• ROI calculation\n• Our services\n• Contact options',
        defaultBot1: 'Thank you for your message! Our specialties are Google Ads, Meta Ads and Performance Marketing.',
        defaultBot2: 'For detailed questions I recommend direct contact with our team:',
        defaultBot3: '📧 maps.werbung@gmail.com or 💬 @Asystentmijbot'
      },
      pl: {
        title: 'Vermarkter Asystent',
        subtitle: 'Jak mogę Ci pomóc?',
        placeholder: 'Napisz swoje pytanie...',
        initialMessage: 'Cześć! Jestem Twoim osobistym asystentem marketingowym. Jak mogę Ci dzisiaj pomóc?',
        googleBtn: '🔍 Google Ads',
        metaBtn: '📱 Meta Ads',
        calculatorBtn: '📊 Kalkulator',
        contactBtn: '💬 Kontakt',
        tooltip: 'Pytania? Pomogę!',
        hint: '💬 Potrzebujesz pomocy? Zapytaj mnie!',
        googleUser: 'Interesuje mnie Google Ads',
        googleBot1: 'Świetnie! Google Ads jest idealny dla gorących leadów z wyszukiwania. Z Performance Max docieramy do Twojej grupy docelowej w całej UE.',
        googleBot2: 'Chciałbyś najpierw przetestować nasz kalkulator ROI, aby zobaczyć, ile możesz zarobić z Google Ads?',
        metaUser: 'Interesuje mnie Meta Ads',
        metaBot1: 'Idealnie! Facebook i Instagram są idealne do generowania leadów i E-Commerce. Używamy remarketingu i Lookalike Audiences dla maksymalnych konwersji.',
        metaBot2: 'Pokazać Ci, jak Meta Ads działa dla Twojego biznesu?',
        calculatorUser: 'Pokaż mi kalkulator',
        calculatorBot: 'Kalkulator ROI pokazuje Ci realne prognozy oparte na rzeczywistych formułach planowania mediów. Możesz testować różne scenariusze.',
        contactUser: 'Chcę się skontaktować',
        contactBot1: 'Bardzo chętnie! Możesz skontaktować się z nami bezpośrednio przez:',
        contactBot2: '📧 Email: maps.werbung@gmail.com',
        contactBot3: '💬 Telegram: @Asystentmijbot',
        contactBot4: 'Lub wypełnij formularz kontaktowy, a skontaktujemy się w ciągu 24 godzin.',
        priceBot1: 'Nasze ceny są przejrzyste i różnią się w zależności od zakresu projektu. Użyj naszego kalkulatora ROI, aby zobaczyć, jakie wyniki są możliwe z Twoim budżetem.',
        priceBot2: 'Chciałbyś osobistej konsultacji? Mogę połączyć Cię z naszym zespołem.',
        helpBot1: 'Chętnie pomogę! Mogę udzielić informacji na temat:',
        helpBot2: '• Kampanie Google Ads & Meta Ads\n• Kalkulacja ROI\n• Nasze usługi\n• Opcje kontaktu',
        defaultBot1: 'Dziękujemy za wiadomość! Nasze specjalności to Google Ads, Meta Ads i Performance Marketing.',
        defaultBot2: 'W szczegółowych pytaniach polecam bezpośredni kontakt z naszym zespołem:',
        defaultBot3: '📧 maps.werbung@gmail.com lub 💬 @Asystentmijbot'
      }
    };

    return translations[this.lang] || translations.de;
  }

  t(key) {
    return this.getTranslation(key);
  }

  init() {
    if (!this.chatbotButton) return;

    // Create chat widget
    this.createChatWidget();

    // Button click handler
    this.chatbotButton.addEventListener('click', () => {
      this.toggleChat();
    });

    // Show tooltip on hover
    this.addTooltip();

    // Auto-open hint after 10 seconds
    this.autoOpenHint();
  }

  createChatWidget() {
    // Create chat container
    const chatContainer = document.createElement('div');
    chatContainer.id = 'chatWidget';
    chatContainer.className = 'chat-widget';
    chatContainer.style.cssText = `
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 380px;
      max-width: calc(100vw - 40px);
      height: 550px;
      max-height: calc(100vh - 120px);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      display: none;
      flex-direction: column;
      z-index: 9999;
      overflow: hidden;
    `;

    // Chat header
    const chatHeader = document.createElement('div');
    chatHeader.className = 'chat-header';
    chatHeader.style.cssText = `
      padding: 16px 20px;
      background: rgba(59, 130, 246, 0.1);
      border-bottom: 1px solid var(--glass-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    `;
    chatHeader.innerHTML = `
      <div>
        <h3 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">${this.t('title')}</h3>
        <p style="margin: 4px 0 0; color: var(--text-secondary); font-size: 0.85rem;">${this.t('subtitle')}</p>
      </div>
      <button id="closeChatBtn" style="background: none; border: none; color: var(--text-secondary); font-size: 1.5rem; cursor: pointer; padding: 0; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">✕</button>
    `;

    // Chat messages
    const chatMessages = document.createElement('div');
    chatMessages.id = 'chatMessages';
    chatMessages.className = 'chat-messages';
    chatMessages.style.cssText = `
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    `;

    // Chat input area
    const chatInputArea = document.createElement('div');
    chatInputArea.className = 'chat-input-area';
    chatInputArea.style.cssText = `
      padding: 16px 20px;
      border-top: 1px solid var(--glass-border);
      background: rgba(0, 0, 0, 0.2);
    `;

    // Quick actions
    const quickActions = document.createElement('div');
    quickActions.id = 'quickActions';
    quickActions.className = 'quick-actions';
    quickActions.style.cssText = `
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    `;

    // Input form
    const inputForm = document.createElement('form');
    inputForm.id = 'chatInputForm';
    inputForm.style.cssText = `
      display: flex;
      gap: 8px;
    `;
    inputForm.innerHTML = `
      <input
        type="text"
        id="chatInput"
        placeholder="${this.t('placeholder')}"
        style="flex: 1; padding: 10px 14px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text-primary); font-size: 0.95rem;"
      >
      <button type="submit" style="padding: 10px 20px; background: var(--brand-blue, #3B82F6); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">→</button>
    `;

    chatInputArea.appendChild(quickActions);
    chatInputArea.appendChild(inputForm);

    chatContainer.appendChild(chatHeader);
    chatContainer.appendChild(chatMessages);
    chatContainer.appendChild(chatInputArea);

    document.body.appendChild(chatContainer);
    this.chatWidget = chatContainer;

    // Event listeners
    document.getElementById('closeChatBtn').addEventListener('click', () => this.toggleChat());
    inputForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleUserMessage();
    });

    // Initial message
    this.addBotMessage(this.t('initialMessage'));
    this.showQuickActions();
  }

  toggleChat() {
    this.isOpen = !this.isOpen;

    if (this.isOpen) {
      this.chatWidget.style.display = 'flex';
      document.getElementById('chatInput')?.focus();

      // Track event
      if (typeof trackEvent === 'function') {
        trackEvent('Chatbot', 'Open', 'Chat Widget Opened');
      }
    } else {
      this.chatWidget.style.display = 'none';
    }
  }

  addMessage(text, type = 'bot') {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-message-${type}`;
    messageDiv.style.cssText = `
      max-width: 80%;
      padding: 12px 16px;
      border-radius: 12px;
      font-size: 0.95rem;
      line-height: 1.5;
      white-space: pre-line;
      ${type === 'bot'
        ? 'background: rgba(59, 130, 246, 0.15); color: var(--text-primary); align-self: flex-start;'
        : 'background: var(--brand-blue, #3B82F6); color: white; align-self: flex-end;'
      }
    `;
    messageDiv.textContent = text;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    this.messages.push({ text, type, timestamp: new Date() });
  }

  addBotMessage(text) {
    this.addMessage(text, 'bot');
  }

  addUserMessage(text) {
    this.addMessage(text, 'user');
  }

  showQuickActions() {
    const quickActions = document.getElementById('quickActions');
    if (!quickActions) return;

    const actions = [
      { text: this.t('googleBtn'), action: 'google' },
      { text: this.t('metaBtn'), action: 'meta' },
      { text: this.t('calculatorBtn'), action: 'calculator' },
      { text: this.t('contactBtn'), action: 'contact' }
    ];

    quickActions.innerHTML = '';
    actions.forEach(action => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = action.text;
      btn.style.cssText = `
        padding: 8px 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        color: var(--text-primary);
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
      `;
      btn.onmouseenter = () => {
        btn.style.background = 'rgba(59, 130, 246, 0.2)';
        btn.style.borderColor = 'rgba(59, 130, 246, 0.4)';
      };
      btn.onmouseleave = () => {
        btn.style.background = 'rgba(255, 255, 255, 0.05)';
        btn.style.borderColor = 'rgba(255, 255, 255, 0.1)';
      };
      btn.addEventListener('click', () => this.handleQuickAction(action.action));
      quickActions.appendChild(btn);
    });
  }

  handleQuickAction(action) {
    switch (action) {
      case 'google':
        this.addUserMessage(this.t('googleUser'));
        this.addBotMessage(this.t('googleBot1'));
        this.addBotMessage(this.t('googleBot2'));
        break;

      case 'meta':
        this.addUserMessage(this.t('metaUser'));
        this.addBotMessage(this.t('metaBot1'));
        this.addBotMessage(this.t('metaBot2'));
        break;

      case 'calculator':
        this.addUserMessage(this.t('calculatorUser'));
        this.addBotMessage(this.t('calculatorBot'));
        setTimeout(() => {
          window.location.href = '#calculator-section';
          this.toggleChat();
        }, 1500);
        break;

      case 'contact':
        this.addUserMessage(this.t('contactUser'));
        this.addBotMessage(this.t('contactBot1'));
        this.addBotMessage(this.t('contactBot2'));
        this.addBotMessage(this.t('contactBot3'));
        this.addBotMessage(this.t('contactBot4'));
        // REMOVED: No redirect to #contact
        break;
    }
  }

  handleUserMessage() {
    const input = document.getElementById('chatInput');
    if (!input || !input.value.trim()) return;

    const userText = input.value.trim();
    this.addUserMessage(userText);
    input.value = '';

    // Simple keyword-based responses
    setTimeout(() => {
      this.generateResponse(userText);
    }, 500);
  }

  generateResponse(text) {
    const lowerText = text.toLowerCase();

    // Check for price keywords in multiple languages
    const priceKeywords = ['preis', 'kosten', 'budget', 'ціна', 'вартість', 'бюджет', 'price', 'cost', 'cena', 'koszt'];
    if (priceKeywords.some(kw => lowerText.includes(kw))) {
      this.addBotMessage(this.t('priceBot1'));
      this.addBotMessage(this.t('priceBot2'));

    } else if (lowerText.includes('google') || lowerText.includes('ads') || lowerText.includes('werbung') || lowerText.includes('реклама')) {
      this.handleQuickAction('google');

    } else if (lowerText.includes('facebook') || lowerText.includes('instagram') || lowerText.includes('meta')) {
      this.handleQuickAction('meta');

    } else if (lowerText.includes('rechner') || lowerText.includes('kalkulator') || lowerText.includes('калькулятор') || lowerText.includes('calculator') || lowerText.includes('roi')) {
      this.handleQuickAction('calculator');

    } else if (lowerText.includes('kontakt') || lowerText.includes('email') || lowerText.includes('telegram') || lowerText.includes('contact')) {
      this.handleQuickAction('contact');

    } else if (lowerText.includes('hilfe') || lowerText.includes('frage') || lowerText.includes('допомога') || lowerText.includes('help') || lowerText.includes('pomoc')) {
      this.addBotMessage(this.t('helpBot1'));
      this.addBotMessage(this.t('helpBot2'));
      this.showQuickActions();

    } else {
      this.addBotMessage(this.t('defaultBot1'));
      this.addBotMessage(this.t('defaultBot2'));
      this.addBotMessage(this.t('defaultBot3'));
    }
  }

  addTooltip() {
    const tooltip = document.createElement('div');
    tooltip.className = 'chatbot-tooltip';
    tooltip.textContent = this.t('tooltip');
    tooltip.style.cssText = `
      position: fixed;
      bottom: 90px;
      right: 20px;
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      color: var(--text-primary);
      padding: 10px 16px;
      border-radius: 8px;
      font-size: 14px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
      z-index: 9998;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;
    document.body.appendChild(tooltip);

    this.chatbotButton.addEventListener('mouseenter', () => {
      if (!this.isOpen) tooltip.style.opacity = '1';
    });

    this.chatbotButton.addEventListener('mouseleave', () => {
      tooltip.style.opacity = '0';
    });
  }

  autoOpenHint() {
    if (localStorage.getItem('chatbot_hint_shown')) return;

    setTimeout(() => {
      if (!this.isOpen) {
        const hint = document.createElement('div');
        hint.style.cssText = `
          position: fixed;
          bottom: 90px;
          right: 20px;
          background: var(--brand-blue, #3B82F6);
          color: white;
          padding: 12px 18px;
          border-radius: 12px;
          font-size: 0.95rem;
          box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
          z-index: 9998;
          animation: slideInRight 0.5s ease;
          cursor: pointer;
        `;
        hint.textContent = this.t('hint');
        hint.onclick = () => {
          this.toggleChat();
          hint.remove();
        };

        document.body.appendChild(hint);

        setTimeout(() => {
          hint.style.transition = 'opacity 0.5s ease';
          hint.style.opacity = '0';
          setTimeout(() => hint.remove(), 500);
        }, 5000);

        localStorage.setItem('chatbot_hint_shown', 'true');
      }
    }, 10000);
  }
}

// Initialize chatbot when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new VermarkterChatbot();
  });
} else {
  new VermarkterChatbot();
}
