/**
 * VERMARKTER - TELEGRAM SERVICE
 * Secure Telegram integration via Supabase Edge Functions
 */

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

// Supabase Configuration
const SUPABASE_URL = 'https://cinufkskitdiuonfibtt.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndydmRidmVraXRlb3BrZHd4dXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjU5MjAsImV4cCI6MjA3ODY0MTkyMH0.ZeUzRVMA2O8oz9_VWkOaKGB8CESnXut9Fb1GminWE_c';

class TelegramService {
  constructor() {
    this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }

  /**
   * Main message sending function
   */
  async sendMessage(message, contact = null, type = 'chat', metadata = {}) {
    try {
      const { data, error } = await this.supabase.functions.invoke('telegram-proxy', {
        body: { message, contact, type, metadata }
      });
      if (error) throw error;
      console.log('✅ Повідомлення надіслано');
      return { success: true, data };
    } catch (err) {
      console.error('❌ Помилка відправки:', err);
      return { success: false, error: err.message };
    }
  }

  /**
   * Send form submission to Telegram
   */
  async sendFormSubmission(formData) {
    const text = `📬 Нова заявка з форми

👤 Ім'я: ${formData.name}
📧 Email: ${formData.email}
📱 Тел: ${formData.phone || 'Не вказано'}
💬 Повідомлення: ${formData.message}

🌐 Мова: ${this.detectLanguage().toUpperCase()}
🕒 ${new Date().toISOString()}`;

    return await this.sendMessage(text, formData.email, 'form', {
      name: formData.name,
      email: formData.email,
      phone: formData.phone
    });
  }

  /**
   * Send calculator results to Telegram
   */
  async sendCalculatorResults(results, contact) {
    const text = `📊 Результат калькулятора

💰 Бюджет: €${results.budget}
📈 Прибуток: €${results.profit}
🎯 ROAS: ${results.roas}%
📧 Контакт: ${contact || 'Не вказано'}

🕒 ${new Date().toISOString()}`;

    return await this.sendMessage(text, contact, 'calculator', results);
  }

  /**
   * Send chat message to Telegram
   */
  async sendChatMessage(userMessage, userContact = null) {
    const lang = this.detectLanguage();
    const text = `💬 Chatbot (${lang.toUpperCase()})

${userMessage}

${userContact ? `📧 Контакт: ${userContact}` : ''}
🕒 ${new Date().toISOString()}`;

    return await this.sendMessage(text, userContact, 'chat', { language: lang });
  }

  /**
   * Detect page language
   */
  detectLanguage() {
    const path = window.location.pathname;
    if (path.includes('/ua/')) return 'ua';
    if (path.includes('/de/')) return 'de';
    if (path.includes('/en/')) return 'en';
    if (path.includes('/pl/')) return 'pl';
    if (path.includes('/ru/')) return 'ru';
    if (path.includes('/tr/')) return 'tr';
    return 'de'; // Default
  }
}

// Create global instance
window.telegramService = new TelegramService();
console.log('✅ Telegram service loaded');
