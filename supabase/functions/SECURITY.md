# Security Hardening Documentation

## Overview
This document describes the comprehensive security measures implemented across all Edge Functions and contact forms to protect against common web vulnerabilities and attacks.

## Edge Functions Security

### 1. Strict CORS Policy
**Implementation:** Both `ai-chat` and `telegram-proxy` functions

**Allowed Origins:**
- `https://vermarkter.eu` (Production)
- `https://www.vermarkter.eu` (Production with www)
- `http://localhost:3000` (Development)
- `http://localhost:5500` (Development - Live Server)
- `http://127.0.0.1:5500` (Development)
- `http://127.0.0.1:3000` (Development)

**Features:**
- Origin validation on every request
- Referer header fallback check
- Rejects requests from unauthorized domains (403 Forbidden)
- Proper CORS preflight handling

**Update Instructions:**
To add your production domain, update the `ALLOWED_ORIGINS` array in both functions:
```typescript
const ALLOWED_ORIGINS = [
  'https://yourdomain.com',  // Add your domain here
  // ... existing origins
]
```

### 2. Input Sanitation
**Implementation:** All user inputs are sanitized before processing

**Protection Against:**
- XSS (Cross-Site Scripting)
- HTML injection
- Script injection

**Sanitation Rules:**
1. Remove all `<script>` tags and content
2. Strip HTML tags using regex
3. Decode HTML entities
4. Limit maximum length to 1000 characters
5. Trim whitespace

**Example:**
```typescript
// Input: "Hello <script>alert('xss')</script> World"
// Output: "Hello  World"
```

### 3. Rate Limiting
**Implementation:** IP-based rate limiting on both functions

**Configuration:**
- **Max Requests:** 3 per minute per IP address
- **Window:** 60 seconds (60000ms)
- **Response:** 429 Too Many Requests

**How It Works:**
1. Tracks request count per IP address
2. Resets counter after time window expires
3. Blocks excessive requests from same IP
4. Uses in-memory storage (Map)

**Note:** For production with multiple instances, consider using Redis or Supabase database for distributed rate limiting.

### 4. Honeypot Protection
**Implementation:** All 32 contact forms across the website

**How It Works:**
1. Hidden field `name="honeypot"` in all forms
2. Positioned off-screen (invisible to humans)
3. Bots typically fill all fields
4. Backend checks if honeypot field is filled
5. If filled → silently reject (return success to fool bots)

**Form Implementation:**
```html
<!-- Honeypot field for bot protection -->
<div style="position: absolute; left: -5000px;" aria-hidden="true">
    <input type="text" name="honeypot" id="honeypot" tabindex="-1" autocomplete="off" />
</div>
```

**Backend Validation:**
```typescript
if (honeypot && honeypot.trim() !== '') {
  // Bot detected - return fake success
  return new Response(
    JSON.stringify({ success: true }),
    { status: 200 }
  )
}
```

## Environment Variables Required

### ai-chat Function
- `GEMINI_API_KEY` - Google Gemini API key for AI responses

### telegram-proxy Function
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHAT_ID` - Chat ID where messages should be sent

**Setup Instructions:**
```bash
# Set environment variables in Supabase dashboard
supabase secrets set GEMINI_API_KEY=your_gemini_api_key
supabase secrets set TELEGRAM_BOT_TOKEN=your_telegram_bot_token
supabase secrets set TELEGRAM_CHAT_ID=your_chat_id
```

## Deployment

### Deploy Edge Functions
```bash
# Deploy ai-chat function
supabase functions deploy ai-chat

# Deploy telegram-proxy function
supabase functions deploy telegram-proxy
```

### Test Security
```bash
# Test rate limiting
curl -X POST https://your-project.supabase.co/functions/v1/ai-chat \
  -H "Origin: https://vermarkter.eu" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "language": "en"}'

# Test unauthorized origin (should return 403)
curl -X POST https://your-project.supabase.co/functions/v1/ai-chat \
  -H "Origin: https://malicious-site.com" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Test honeypot (should return fake success)
curl -X POST https://your-project.supabase.co/functions/v1/telegram-proxy \
  -H "Origin: https://vermarkter.eu" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "test@test.com", "message": "Hello", "honeypot": "bot-filled"}'
```

## Files Modified

### Edge Functions (2 files)
- `supabase/functions/ai-chat/index.ts` - Hardened with security features
- `supabase/functions/telegram-proxy/index.ts` - NEW - Created with security built-in

### HTML Forms (32 files)
All contact forms across 6 languages now include honeypot fields:
- DE: 6 files (google-ads, meta-ads, tiktok-ads, crm-integration, seo, index)
- EN: 6 files (google-ads, meta-ads, tiktok-ads, crm-integration, seo, index)
- PL: 6 files (google-ads, meta-ads, tiktok-ads, crm-integration, seo, index)
- RU: 6 files (google-ads, meta-ads, tiktok-ads, crm-integration, seo, index)
- UA: 4 files (google-ads, meta-ads, tiktok-ads, index)
- TR: 4 files (google-ads, meta-ads, tiktok-ads, index)

## Security Best Practices

### 1. Keep Environment Variables Secret
- Never commit API keys or tokens to Git
- Use Supabase secrets management
- Rotate keys regularly

### 2. Monitor Rate Limits
- Check logs for rate limit violations
- Adjust limits based on legitimate usage patterns
- Consider implementing CAPTCHA for repeated violations

### 3. Review Honeypot Catches
- Monitor how many bots are caught
- Analyze patterns to improve detection
- Consider adding more honeypot variants

### 4. Update Allowed Origins
- Add production domain before going live
- Remove development origins in production
- Keep list minimal (principle of least privilege)

### 5. Input Validation
- Always sanitize user input
- Validate email format on backend
- Check message length limits
- Never trust client-side validation alone

## Troubleshooting

### Issue: Legitimate requests blocked (403)
**Solution:** Check if origin is in `ALLOWED_ORIGINS` array. Add it if needed.

### Issue: Rate limit too restrictive
**Solution:** Increase `RATE_LIMIT_MAX` or `RATE_LIMIT_WINDOW` values.

### Issue: Honeypot catching real users
**Solution:** Verify honeypot field is properly hidden with CSS. Check browser compatibility.

### Issue: CORS errors in browser console
**Solution:** Ensure origin matches exactly (with/without www, http/https).

## Additional Security Measures (Future Enhancements)

1. **Distributed Rate Limiting** - Use Redis or Supabase DB for multi-instance rate limiting
2. **IP Reputation Checks** - Integrate with IP reputation services
3. **CAPTCHA Integration** - Add reCAPTCHA for high-risk actions
4. **Request Signing** - Implement HMAC signatures for API requests
5. **Anomaly Detection** - Machine learning for unusual behavior patterns
6. **WAF Integration** - Use Cloudflare or AWS WAF for additional protection

## Contact & Support
For security concerns or questions:
- Review logs in Supabase dashboard
- Check function execution logs
- Test with curl commands above
- Update security rules as needed

Last Updated: 2026-02-06
