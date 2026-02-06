// Supabase Edge Function: Telegram Proxy with Security Hardening
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const TELEGRAM_BOT_TOKEN = Deno.env.get('TELEGRAM_BOT_TOKEN')
const TELEGRAM_CHAT_ID = Deno.env.get('TELEGRAM_CHAT_ID')

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

// Rate limiting storage (simple in-memory for now)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>()
const RATE_LIMIT_MAX = 3 // Max requests per minute
const RATE_LIMIT_WINDOW = 60000 // 1 minute in ms

// Security Helper Functions
function sanitizeInput(text: string): string {
  if (!text) return ''

  // Remove HTML tags and script content
  let cleaned = text.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
  cleaned = cleaned.replace(/<[^>]+>/g, '')

  // Decode HTML entities
  cleaned = cleaned.replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  cleaned = cleaned.replace(/&quot;/g, '"').replace(/&#39;/g, "'")

  // Limit length
  return cleaned.substring(0, 1000).trim()
}

function checkRateLimit(ip: string): boolean {
  const now = Date.now()
  const record = rateLimitStore.get(ip)

  if (!record || now > record.resetTime) {
    // New window
    rateLimitStore.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW })
    return true
  }

  if (record.count >= RATE_LIMIT_MAX) {
    return false // Rate limit exceeded
  }

  // Increment count
  record.count++
  rateLimitStore.set(ip, record)
  return true
}

function validateOrigin(req: Request): boolean {
  const origin = req.headers.get('origin')
  const referer = req.headers.get('referer')

  // Check origin
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    return true
  }

  // Check referer as fallback
  if (referer) {
    for (const allowedOrigin of ALLOWED_ORIGINS) {
      if (referer.startsWith(allowedOrigin)) {
        return true
      }
    }
  }

  return false
}

async function sendToTelegram(message: string): Promise<boolean> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.error('Telegram credentials not configured')
    return false
  }

  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: 'HTML'
      })
    })

    return response.ok
  } catch (error) {
    console.error('Telegram API error:', error)
    return false
  }
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
      {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }

  // 2. Rate limiting
  if (!checkRateLimit(clientIP)) {
    console.warn(`Rate limit exceeded for IP: ${clientIP}`)
    return new Response(
      JSON.stringify({ error: 'Too many requests. Please try again later.' }),
      {
        status: 429,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }

  try {
    const body = await req.json()
    const { name, email, phone, message, honeypot, type, language, metadata } = body

    // 3. Honeypot check - if filled, it's a bot
    if (honeypot && honeypot.trim() !== '') {
      console.warn(`Honeypot triggered. IP: ${clientIP}`)
      // Return success to fool bots
      return new Response(
        JSON.stringify({ success: true, message: 'Message sent successfully' }),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': req.headers.get('origin') || ALLOWED_ORIGINS[0]
          }
        }
      )
    }

    // 4. Input sanitation
    const cleanName = sanitizeInput(name || '')
    const cleanEmail = sanitizeInput(email || '')
    const cleanPhone = sanitizeInput(phone || '')
    const cleanMessage = sanitizeInput(message || '')

    // Validate required fields
    if (!cleanName || !cleanEmail || !cleanMessage) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': req.headers.get('origin') || ALLOWED_ORIGINS[0]
          }
        }
      )
    }

    // Build Telegram message
    let telegramMessage = `🔔 <b>New ${type || 'Contact'} Form Submission</b>\n\n`
    telegramMessage += `👤 <b>Name:</b> ${cleanName}\n`
    telegramMessage += `📧 <b>Email:</b> ${cleanEmail}\n`

    if (cleanPhone) {
      telegramMessage += `📱 <b>Phone:</b> ${cleanPhone}\n`
    }

    telegramMessage += `💬 <b>Message:</b>\n${cleanMessage}\n\n`

    if (language) {
      telegramMessage += `🌐 <b>Language:</b> ${language.toUpperCase()}\n`
    }

    if (metadata) {
      telegramMessage += `\n📊 <b>Metadata:</b>\n${JSON.stringify(metadata, null, 2)}\n`
    }

    telegramMessage += `\n🕒 ${new Date().toISOString()}`

    // Send to Telegram
    const sent = await sendToTelegram(telegramMessage)

    if (!sent) {
      throw new Error('Failed to send message to Telegram')
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: 'Message sent successfully'
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
    console.error('Error in telegram-proxy function:', error)

    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        message: 'Failed to process your request. Please try again later.'
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': req.headers.get('origin') || ALLOWED_ORIGINS[0]
        }
      }
    )
  }
})
