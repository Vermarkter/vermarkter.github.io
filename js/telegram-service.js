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
   * Sends directly to telegram-proxy with proper field names
   */
  async sendMessage(formData) {
    // Ensure we send the fields that telegram-proxy expects
    const requestBody = {
      name: formData.name || 'Website Visitor',
      email: formData.email || formData.contact || '',
      phone: formData.phone || '',
      message: formData.message || '',
      type: formData.type || 'chat',
      language: formData.language || this.detectLanguage(),
      metadata: formData.metadata || {},
      honeypot: formData.honeypot || ''
    };

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
    return await this.sendMessage({
      name: formData.name,
      email: formData.email,
      phone: formData.phone || '',
      message: formData.message,
      type: 'form',
      language: this.detectLanguage(),
      honeypot: formData.honeypot || ''
    });
  }

  /**
   * Send calculator results to Telegram
   */
  async sendCalculatorResults(results, contact) {
    const message = `Calculator Results:
Budget: €${results.budget}
Profit: €${results.profit}
ROAS: ${results.roas}%`;

    return await this.sendMessage({
      name: 'Calculator User',
      email: contact || '',
      message: message,
      type: 'calculator',
      language: this.detectLanguage(),
      metadata: results
    });
  }

  /**
   * Send chat message to Telegram
   */
  async sendChatMessage(userMessage, userContact = null) {
    return await this.sendMessage({
      name: 'Chat User',
      email: userContact || '',
      message: userMessage,
      type: 'chat',
      language: this.detectLanguage()
    });
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
