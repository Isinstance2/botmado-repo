# app/utils/twilio_client.py
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(to: str, body: str):
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to
    )
    return message.sid
