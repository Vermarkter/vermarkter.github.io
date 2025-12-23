import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

// 👇 ВСТАВ СЮДИ ТІ ДАНІ, ЩО ТИ СКОПІЮВАВ У НАЛАШТУВАННЯХ SUPABASE (Крок А)
const SUPABASE_URL = 'СЮДИ_ВСТАВ_URL_ПРОЕКТУ'; 
const SUPABASE_ANON_KEY = 'СЮДИ_ВСТАВ_ДОВГИЙ_ANON_KEY'; 

// Ініціалізація (це не чіпай)
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Функція відправки (це не чіпай)
export async function sendToTelegram(message, contactInfo = '') {
    console.log('Відправка в Telegram через Supabase...');
    
    try {
        const { data, error } = await supabase.functions.invoke('telegram-proxy', {
            body: { 
                message: message,
                contact: contactInfo
            }
        });

        if (error) throw error;
        console.log('Успішно:', data);
        return true;
    } catch (error) {
        console.error('Помилка відправки:', error);
        return false;
    }
}
