/**
 * VERMARKTER - Smart Chatbot
 * Acts as agency employee, helps users with services
 */

class VermarkterChatbot {
  constructor() {
    this.chatbotButton = document.getElementById('chatbotButton');
    this.isOpen = false;
    this.init();
  }

  init() {
    if (!this.chatbotButton) return;

    // Click handler - open Telegram bot
    this.chatbotButton.addEventListener('click', () => {
      this.openTelegramBot();
    });

    // Show tooltip on hover
    this.addTooltip();
  }

  openTelegramBot() {
    // Open the Telegram bot in a new window
    window.open('https://t.me/Asystentmijbot', '_blank');

    // Track event if analytics available
    if (typeof trackEvent === 'function') {
      trackEvent('Chatbot', 'Open', 'Telegram Bot Clicked');
    }
  }

  addTooltip() {
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'chatbot-tooltip';
    tooltip.textContent = 'Fragen? Schreib uns!';
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

    // Show/hide tooltip on hover
    this.chatbotButton.addEventListener('mouseenter', () => {
      tooltip.style.opacity = '1';
    });

    this.chatbotButton.addEventListener('mouseleave', () => {
      tooltip.style.opacity = '0';
    });

    // Auto-show tooltip after 5 seconds (first visit hint)
    if (!localStorage.getItem('chatbot_hint_shown')) {
      setTimeout(() => {
        tooltip.style.opacity = '1';
        setTimeout(() => {
          tooltip.style.opacity = '0';
          localStorage.setItem('chatbot_hint_shown', 'true');
        }, 3000);
      }, 5000);
    }
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
