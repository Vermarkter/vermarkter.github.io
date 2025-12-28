// Supabase Edge Function: AI Chat with Gemini
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const GEMINI_API_KEY = Deno.env.get('GEMINI_API_KEY')

// System instructions for different languages
const SYSTEM_INSTRUCTIONS = {
  ua: `Ти — професійний консультант маркетингової агенції Vermarkter.
Твоя ціль: коротко відповісти на питання і запропонувати залишити контакт або перейти до калькулятора.
Наші послуги: Google Ads, Meta Ads, CRM-інтеграція.
Ціни: Старт €399/міс, Зростання €699/міс, Бізнес - індивідуально.
Стиль спілкування: Ввічливий, діловий, лаконічний.
Відповідай українською мовою. Максимум 2-3 речення.`,

  de: `Du bist ein professioneller Berater der Marketing-Agentur Vermarkter.
Dein Ziel: Kurz die Frage beantworten und vorschlagen, Kontakt zu hinterlassen oder zum Rechner zu gehen.
Unsere Dienstleistungen: Google Ads, Meta Ads, CRM-Integration.
Preise: Start €399/Monat, Wachstum €699/Monat, Business - individuell.
Kommunikationsstil: Höflich, geschäftlich, prägnant.
Antworte auf Deutsch. Maximum 2-3 Sätze.`,

  en: `You are a professional consultant of Vermarkter marketing agency.
Your goal: Briefly answer the question and suggest leaving contact or going to the calculator.
Our services: Google Ads, Meta Ads, CRM integration.
Prices: Start €399/month, Growth €699/month, Business - custom.
Communication style: Polite, business-like, concise.
Answer in English. Maximum 2-3 sentences.`,

  pl: `Jesteś profesjonalnym konsultantem agencji marketingowej Vermarkter.
Twój cel: Krótko odpowiedzieć na pytanie i zaproponować pozostawienie kontaktu lub przejście do kalkulatora.
Nasze usługi: Google Ads, Meta Ads, integracja CRM.
Ceny: Start €399/mies, Wzrost €699/mies, Biznes - indywidualnie.
Styl komunikacji: Uprzejmy, biznesowy, zwięzły.
Odpowiadaj po polsku. Maksymalnie 2-3 zdania.`,
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    })
  }

  try {
    const { message, language = 'ua' } = await req.json()

    if (!message) {
      return new Response(
        JSON.stringify({ error: 'Message is required' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        }
      )
    }

    if (!GEMINI_API_KEY) {
      throw new Error('GEMINI_API_KEY not configured')
    }

    // Get system instruction for language
    const systemInstruction = SYSTEM_INSTRUCTIONS[language as keyof typeof SYSTEM_INSTRUCTIONS] || SYSTEM_INSTRUCTIONS.ua

    // Call Gemini API
    const geminiResponse = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: `${systemInstruction}\n\nКлієнт запитує: ${message}`
            }]
          }],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 200,
          }
        })
      }
    )

    if (!geminiResponse.ok) {
      const errorText = await geminiResponse.text()
      console.error('Gemini API error:', errorText)
      throw new Error('Gemini API request failed')
    }

    const geminiData = await geminiResponse.json()

    // Extract response text
    const aiResponse = geminiData.candidates?.[0]?.content?.parts?.[0]?.text ||
      'Зараз я перевантажений, залиште контакти менеджеру.'

    return new Response(
      JSON.stringify({
        reply: aiResponse.trim(),
        success: true
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    )

  } catch (error) {
    console.error('Error in ai-chat function:', error)

    return new Response(
      JSON.stringify({
        reply: 'Зараз я перевантажений, залиште контакти менеджеру.',
        success: false,
        error: error.message
      }),
      {
        status: 200, // Return 200 to avoid breaking frontend
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    )
  }
})
