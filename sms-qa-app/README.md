# SMS Q&A App

An app that automatically responds to text messages using AI.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- **Twilio**: Get credentials from [Twilio Console](https://console.twilio.com)
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### 3. Run the app

```bash
python app.py
```

### 4. Expose your local server

Use ngrok to create a public URL:

```bash
ngrok http 5000
```

### 5. Configure Twilio webhook

1. Go to [Twilio Console](https://console.twilio.com) > Phone Numbers > Your Number
2. Under "Messaging", set the webhook URL to: `https://your-ngrok-url.ngrok.io/sms`
3. Set method to POST

## How it works

1. Someone texts your Twilio phone number
2. Twilio forwards the message to your `/sms` endpoint
3. The app sends the question to OpenAI
4. OpenAI generates a response
5. The response is sent back via SMS

## Deployment

For production, deploy to a cloud platform:

```bash
# Using gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT
```
