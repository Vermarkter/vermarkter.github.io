import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

// 1. Твій URL (я взяв його з твого скріншоту)
const SUPABASE_URL = 'https://cinufkskitdiuonfibtt.supabase.co'; 

// 2. Твій Ключ (Встав сюди той довгий рядок eyJh..., який ти копіював раніше)
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpbnVma3NraXRkaXVvbmZpYnR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxODQ1MzksImV4cCI6MjA4MTc2MDUzOX0.V_IySnKEy-xdBcMkgmNKPAjCeV7nLe8OoLJ_rbe-rRw'; 

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export async function sendToTelegram(message, contactInfo = '') {
    console.log('Sending to Telegram via Supabase...');
    
    try {
        const { data, error } = await supabase.functions.invoke('telegram-proxy', {
            body: { 
                message: message,
                contact: contactInfo
            }
        });

        if (error) throw error;
        console.log('Success:', data);
        return true;
    } catch (error) {
        console.error('Error sending message:', error);
        return false;
    }
}
