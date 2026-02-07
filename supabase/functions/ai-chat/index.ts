// Supabase Edge Function: AI Chat with Gemini (Security Hardened)
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const GEMINI_API_KEY = Deno.env.get('GEMINI_API_KEY')

// Security Configuration
const ALLOWED_ORIGINS = [
  'https://vermarkter.eu',
  'https://www.vermarkter.eu',
  'https://vermarkter.github.io',
  'http://localhost:3000',
  'http://localhost:5500',
  'http://127.0.0.1:5500',
  'http://127.0.0.1:3000'
]

// Rate limiting storage
const rateLimitStore = new Map<string, { count: number; resetTime: number }>()
const RATE_LIMIT_MAX = 3
const RATE_LIMIT_WINDOW = 60000

// Security Helper Functions
function sanitizeInput(text: string): string {
  if (!text) return ''
  let cleaned = text.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
  cleaned = cleaned.replace(/<[^>]+>/g, '')
  cleaned = cleaned.replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  cleaned = cleaned.replace(/&quot;/g, '"').replace(/&#39;/g, "'")
  return cleaned.substring(0, 1000).trim()
}

function checkRateLimit(ip: string): boolean {
  const now = Date.now()
  const record = rateLimitStore.get(ip)
  if (!record || now > record.resetTime) {
    rateLimitStore.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
    return true
  }
  if (record.count >= RATE_LIMIT_MAX) return false
  record.count++
  rateLimitStore.set(ip, record)
  return true
}

function validateOrigin(req: Request): boolean {
  const origin = req.headers.get('origin')
  const referer = req.headers.get('referer')
  if (origin && ALLOWED_ORIGINS.includes(origin)) return true
  if (referer) {
    for (const allowedOrigin of ALLOWED_ORIGINS) {
      if (referer.startsWith(allowedOrigin)) return true
    }
  }
  return false
}

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

  ru: `Ты — профессиональный консультант маркетингового агентства Vermarkter.
Твоя цель: кратко ответить на вопрос и предложить оставить контакт или перейти к калькулятору.
Наши услуги: Google Ads, Meta Ads, CRM-интеграция.
Цены: Старт €399/мес, Рост €699/мес, Бизнес - индивидуально.
Стиль общения: Вежливый, деловой, лаконичный.
Отвечай на русском языке. Максимум 2-3 предложения.`,

  tr: `Sen Vermarkter pazarlama ajansının profesyonel danışmanısın.
Amacın: Soruyu kısaca cevaplamak ve iletişim bırakmayı veya hesap makinesine gitmeyi önermek.
Hizmetlerimiz: Google Ads, Meta Ads, CRM entegrasyonu.
Fiyatlar: Başlangıç €399/ay, Büyüme €699/ay, İş - özel.
İletişim tarzı: Nazik, iş odaklı, özlü.
Türkçe cevap ver. Maksimum 2-3 cümle.`,
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    const origin = req.headers.get('origin')
    const allowedOrigin = ALLOWED_ORIGINS.includes(origin || '') ? origin : ALLOWED_ORIGINS[0]

    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': allowedOrigin || '',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400',
      },
    })
  }

  // Security checks
  const clientIP = req.headers.get('x-forwarded-for') || req.headers.get('x-real-ip') || 'unknown'

  // 1. Validate origin/referer
  if (!validateOrigin(req)) {
    console.warn(`Blocked request from unauthorized origin. IP: ${clientIP}`)
    return new Response(
      JSON.stringify({ error: 'Unauthorized origin' }),
      { status: 403, headers: { 'Content-Type': 'application/json' } }
    )
  }

  // 2. Rate limiting
  if (!checkRateLimit(clientIP)) {
    console.warn(`Rate limit exceeded for IP: ${clientIP}`)
    return new Response(
      JSON.stringify({ error: 'Too many requests. Please try again later.' }),
      { status: 429, headers: { 'Content-Type': 'application/json' } }
    )
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
            'Access-Control-Allow-Origin': req.headers.get('origin') || ALLOWED_ORIGINS[0]
          }
        }
      )
    }

    // 3. Input sanitation
    const cleanMessage = sanitizeInput(message)

    if (!GEMINI_API_KEY) {
      throw new Error('GEMINI_API_KEY not configured')
    }

    // Get system instruction for language
    const systemInstruction = SYSTEM_INSTRUCTIONS[language as keyof typeof SYSTEM_INSTRUCTIONS] || SYSTEM_INSTRUCTIONS.ua

    // Call Gemini API with sanitized message
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
              text: `${systemInstruction}\n\nКлієнт запитує: ${cleanMessage}`
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
          'Access-Control-Allow-Origin': req.headers.get('origin') || ALLOWED_ORIGINS[0]
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
          'Access-Control-Allow-Origin': req.headers.get('origin') || ALLOWED_ORIGINS[0]
        }
      }
    )
  }
})
