"""
SMS Q&A App - Automatically responds to text messages using AI
"""

import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# System prompt for the AI
SYSTEM_PROMPT = """You are a helpful assistant responding to text messages.
Keep your responses concise and friendly since they will be sent via SMS.
Aim for responses under 160 characters when possible, but be thorough when needed.
Be direct and helpful."""


def get_ai_response(question: str) -> str:
    """Generate an AI response to the user's question."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "Sorry, I couldn't process your question. Please try again."


@app.route("/sms", methods=["POST"])
def sms_reply():
    """Handle incoming SMS messages and respond with AI-generated answers."""
    # Get the incoming message
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "")

    print(f"Received message from {from_number}: {incoming_msg}")

    # Generate AI response
    ai_response = get_ai_response(incoming_msg)

    print(f"Responding with: {ai_response}")

    # Create Twilio response
    resp = MessagingResponse()
    resp.message(ai_response)

    return str(resp)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sms-qa-app"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print(f"Starting SMS Q&A App on port {port}")
    print("Webhook URL: /sms (POST)")

    app.run(host="0.0.0.0", port=port, debug=debug)
