# Supabase Edge Functions - Setup Instructions

## Prerequisites

1. Install Supabase CLI:
```bash
npm install -g supabase
```

2. Login to Supabase:
```bash
supabase login
```

3. Link your project:
```bash
supabase link --project-ref YOUR_PROJECT_REF
```

## Deploy ai-chat Function

### 1. Set Environment Variables

Add `GEMINI_API_KEY` to your Supabase project:

```bash
supabase secrets set GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Deploy Function

```bash
supabase functions deploy ai-chat
```

### 3. Get Function URL

After deployment, your function will be available at:
```
https://YOUR_PROJECT_REF.supabase.co/functions/v1/ai-chat
```

### 4. Update Frontend

In `JS/chatbot.js`, replace the placeholder URL on line 528:

```javascript
const response = await fetch('https://YOUR_SUPABASE_PROJECT.supabase.co/functions/v1/ai-chat', {
```

With your actual Supabase project URL:

```javascript
const response = await fetch('https://YOUR_PROJECT_REF.supabase.co/functions/v1/ai-chat', {
```

## Testing

Test the function locally:

```bash
supabase functions serve ai-chat
```

Then test with curl:

```bash
curl -X POST http://localhost:54321/functions/v1/ai-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Скільки коштує Google Ads?", "language": "ua"}'
```

## Get Gemini API Key

1. Go to https://ai.google.dev/
2. Click "Get API key"
3. Create a new project or select existing
4. Generate API key
5. Copy the key and set it in Supabase secrets

## Troubleshooting

### Check function logs:
```bash
supabase functions logs ai-chat
```

### View secrets:
```bash
supabase secrets list
```

### Redeploy:
```bash
supabase functions deploy ai-chat --no-verify-jwt
```
