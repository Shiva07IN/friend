# AI Girlfriend Instagram Bot

Fast AI-powered Instagram chatbot with personality.

## Features
- ⚡ Ultra-fast responses (0.5s check interval)
- 💾 Full conversation history (20 messages)
- 🤖 Groq AI (llama-3.1-8b-instant)
- 💕 Flirty, cute personality

## Deploy to Railway

1. Fork this repo
2. Go to [Railway.app](https://railway.app)
3. Create new project from GitHub
4. Add environment variables:
   - `INSTAGRAM_USERNAME`
   - `INSTAGRAM_PASSWORD`
   - `GROQ_API_KEY`
5. Deploy!

## Local Setup

```bash
pip install -r requirements.txt
export INSTAGRAM_USERNAME=your_username
export INSTAGRAM_PASSWORD=your_password
export GROQ_API_KEY=your_key
python ai_girlfriend_bot.py
```

## Get API Key
- Groq: https://console.groq.com/keys (FREE)
