/**
 * VERMARKTER - TELEGRAM SERVICE
 * Secure Telegram integration via Supabase Edge Functions
 *
 * DEBUG MODE: Enabled for troubleshooting
 */

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

// Supabase Configuration
const SUPABASE_URL = 'https://cinufkskitdiuonfibtt.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpbnVma3NraXRkaXVvbmZpYnR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxODQ1MzksImV4cCI6MjA4MTc2MDUzOX0.V_IySnKEy-xdBcMkgmNKPAjCeV7nLe8OoLJ_rbe-rRw';

// Debug flag
const DEBUG = true;

class TelegramService {
  constructor() {
    this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    this.functionUrl = `${SUPABASE_URL}/functions/v1/telegram-proxy`;

    if (DEBUG) {
      console.log('🔧 TelegramService initialized');
      console.log('🔧 Supabase URL:', SUPABASE_URL);
      console.log('🔧 Function URL:', this.functionUrl);
    }
  }

  /**
   * Main message sending function with detailed debugging
   */
  async sendMessage(message, contact = null, type = 'chat', metadata = {}) {
    const requestBody = { message, contact, type, metadata };

    if (DEBUG) {
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('📤 TELEGRAM SERVICE - SENDING MESSAGE');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('🎯 Function:', 'telegram-proxy');
      console.log('📧 Contact:', contact);
      console.log('📝 Type:', type);
      console.log('📦 Request Body:', JSON.stringify(requestBody, null, 2));
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    }

    try {
      const { data, error } = await this.supabase.functions.invoke('telegram-proxy', {
        body: requestBody
      });

      if (DEBUG) {
        console.log('📥 RESPONSE RECEIVED');
        console.log('✅ Data:', JSON.stringify(data, null, 2));
        if (error) console.log('❌ Error:', JSON.stringify(error, null, 2));
      }

      if (error) {
        console.error('❌ Supabase Function Error:', error);
        throw error;
      }

      console.log('✅ Повідомлення успішно надіслано!');
      return { success: true, data };

    } catch (err) {
      console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.error('❌ TELEGRAM SERVICE - ERROR');
      console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.error('Error message:', err.message);
      console.error('Full error:', err);
      console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
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
