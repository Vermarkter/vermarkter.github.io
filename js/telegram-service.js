/**
 * VERMARKTER - TELEGRAM SERVICE
 * Secure Telegram integration via Supabase Edge Functions
 */

// 👇 ТВОЇ ДАНІ SUPABASE
const MY_SUPABASE_URL = 'https://cinufkskitdiuonfibtt.supabase.co'; 
const MY_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpbnVma3NraXRkaXVvbmZpYnR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxODQ1MzksImV4cCI6MjA4MTc2MDUzOX0.V_IySnKEy-xdBcMkgmNKPAjCeV7nLe8OoLJ_rbe-rRw'; 

class TelegramService {
  constructor() {
    this.SUPABASE_URL = MY_SUPABASE_URL;
    this.SUPABASE_ANON_KEY = MY_ANON_KEY;

    this.initialized = false;
    this.supabaseClient = null;
  }

  /**
   * Ініціалізація Supabase
   */
  init() {
    if (this.initialized) return;

    // Перевірка, чи підключена бібліотека Supabase в HTML
    if (typeof window.supabase === 'undefined') {
      console.error('❌ Supabase library not loaded. Add <script> tag to HTML.');
      return;
    }

    try {
      this.supabaseClient = window.supabase.createClient(
        this.SUPABASE_URL,
        this.SUPABASE_ANON_KEY
      );
      this.initialized = true;
      console.log('✅ Telegram service initialized');
    } catch (error) {
      console.error('❌ Failed to initialize Supabase:', error);
    }
  }

  /**
   * Головна функція відправки
   */
  async sendMessage(message, contact = null, type = 'chat', metadata = {}) {
    if (!this.initialized) this.init();

    if (!this.initialized) {
        console.error('Supabase не ініціалізовано');
        return { success: false };
    }

    try {
      // Виклик Edge Function 'telegram-proxy'
      const { data, error } = await this.supabaseClient.functions.invoke('telegram-proxy', {
        body: {
          message: message,
          contact: contact,
          type: type,
          metadata: metadata
        }
      });

      if (error) throw error;
      console.log('✅ Message sent successfully:', data);
      return { success: true, data };

    } catch (error) {
      console.error('❌ Network error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Відправка повідомлення з ЧАТУ
   */
  async sendChatMessage(userMessage, userContact = null) {
    const lang = this.detectLanguage();
    const message = `
💬 Chatbot (${lang.toUpperCase()})
---------------------------
${userMessage}
---------------------------
${userContact ? `Kontakt: ${userContact}` : ''}
    `.trim();

    return await this.sendMessage(message, userContact, 'chat', { language: lang });
  }

  /**
   * Відправка результатів КАЛЬКУЛЯТОРА
   */
  async sendCalculatorResults(budget, results, userContact = null) {
    const message = `
📊 ROI Calculator
---------------------------
Budget: €${budget}
Clicks: ${results.clicks}
Leads: ${results.conversions}
Profit: €${results.profit}
ROAS: ${results.roas}x
    `.trim();

    return await this.sendMessage(message, userContact, 'calculator', results);
  }

  /**
   * Визначення мови сторінки
   */
  detectLanguage() {
    const path = window.location.pathname;
    if (path.includes('/ua/')) return 'ua';
    if (path.includes('/de/')) return 'de';
    if (path.includes('/en/')) return 'en';
    if (path.includes('/pl/')) return 'pl';
    return 'de'; // За замовчуванням
  }
}

// Створюємо глобальний об'єкт
window.telegramService = new TelegramService();

// Автозапуск
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.telegramService.init();
  });
} else {
  window.telegramService.init();
}