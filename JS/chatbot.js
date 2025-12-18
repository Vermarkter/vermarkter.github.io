/**
 * VERMARKTER - Smart Chatbot
 * Text-based assistant that acts as agency employee
 * Helps users understand services and guides to contact
 */

class VermarkterChatbot {
  constructor() {
    this.chatbotButton = document.getElementById('chatbotButton');
    this.isOpen = false;
    this.messages = [];
    this.chatWidget = null;

    this.init();
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
        <h3 style="margin: 0; color: var(--text-primary); font-size: 1.1rem;">Vermarkter Assistant</h3>
        <p style="margin: 4px 0 0; color: var(--text-secondary); font-size: 0.85rem;">Wie kann ich Ihnen helfen?</p>
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
        placeholder="Schreiben Sie Ihre Frage..."
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
    this.addBotMessage('Hallo! Ich bin Ihr persönlicher Marketing-Assistent. Wie kann ich Ihnen heute helfen?');
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
      { text: '🔍 Google Ads', action: 'google' },
      { text: '📱 Meta Ads', action: 'meta' },
      { text: '📊 Kalkulator', action: 'calculator' },
      { text: '💬 Kontakt', action: 'contact' }
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
        this.addUserMessage('Ich interessiere mich für Google Ads');
        this.addBotMessage('Großartig! Google Ads ist perfekt für heiße Leads aus der Suche. Mit Performance Max erreichen wir Ihre Zielgruppe in der gesamten EU.');
        this.addBotMessage('Möchten Sie zuerst unseren ROI-Rechner testen, um zu sehen, wie viel Sie mit Google Ads verdienen können?');
        break;

      case 'meta':
        this.addUserMessage('Ich interessiere mich für Meta Ads');
        this.addBotMessage('Perfekt! Facebook & Instagram sind ideal für Leadgenerierung und E-Commerce. Wir nutzen Remarketing und Lookalike-Audiences für maximale Conversions.');
        this.addBotMessage('Soll ich Ihnen zeigen, wie Meta Ads für Ihr Business funktioniert?');
        break;

      case 'calculator':
        this.addUserMessage('Zeig mir den Kalkulator');
        this.addBotMessage('Der ROI-Rechner zeigt Ihnen reale Prognosen basierend auf echten Mediaplanung-Formeln. Sie können verschiedene Szenarien testen.');
        setTimeout(() => {
          window.location.href = '#calculator-section';
          this.toggleChat();
        }, 1500);
        break;

      case 'contact':
        this.addUserMessage('Ich möchte Kontakt aufnehmen');
        this.addBotMessage('Sehr gerne! Sie können uns direkt erreichen über:');
        this.addBotMessage('📧 Email: maps.werbung@gmail.com');
        this.addBotMessage('💬 Telegram: @Asystentmijbot');
        this.addBotMessage('Oder füllen Sie das Kontaktformular aus, und wir melden uns innerhalb von 24 Stunden.');
        setTimeout(() => {
          window.location.href = '#contact';
        }, 2000);
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

    if (lowerText.includes('preis') || lowerText.includes('kosten') || lowerText.includes('budget')) {
      this.addBotMessage('Unsere Preise sind transparent und variieren je nach Projektumfang. Nutzen Sie unseren ROI-Rechner, um zu sehen, welche Ergebnisse mit Ihrem Budget möglich sind.');
      this.addBotMessage('Möchten Sie eine persönliche Beratung? Ich kann Sie mit unserem Team verbinden.');

    } else if (lowerText.includes('google') || lowerText.includes('ads') || lowerText.includes('werbung')) {
      this.handleQuickAction('google');

    } else if (lowerText.includes('facebook') || lowerText.includes('instagram') || lowerText.includes('meta')) {
      this.handleQuickAction('meta');

    } else if (lowerText.includes('rechner') || lowerText.includes('kalkulator') || lowerText.includes('roi')) {
      this.handleQuickAction('calculator');

    } else if (lowerText.includes('kontakt') || lowerText.includes('email') || lowerText.includes('telegram')) {
      this.handleQuickAction('contact');

    } else if (lowerText.includes('hilfe') || lowerText.includes('frage')) {
      this.addBotMessage('Ich helfe Ihnen gerne! Ich kann Ihnen Informationen geben zu:');
      this.addBotMessage('• Google Ads & Meta Ads Kampagnen\n• ROI-Berechnung\n• Unsere Services\n• Kontaktmöglichkeiten');
      this.showQuickActions();

    } else {
      this.addBotMessage('Danke für Ihre Nachricht! Unsere Spezialgebiete sind Google Ads, Meta Ads und Performance-Marketing.');
      this.addBotMessage('Für detaillierte Fragen empfehle ich einen direkten Kontakt mit unserem Team:');
      this.addBotMessage('📧 maps.werbung@gmail.com oder 💬 @Asystentmijbot');
    }
  }

  addTooltip() {
    const tooltip = document.createElement('div');
    tooltip.className = 'chatbot-tooltip';
    tooltip.textContent = 'Fragen? Ich helfe Ihnen!';
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
        hint.textContent = '💬 Brauchen Sie Hilfe? Fragen Sie mich!';
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
