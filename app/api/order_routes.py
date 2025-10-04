# order_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.utils.whatsapp_handler import TwilioWhatsAppHandler

router = APIRouter()
whatsapp_handler = TwilioWhatsAppHandler()

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    incoming_msg = form.get("Body", "")
    from_number = form.get("From", "")
    if not incoming_msg or not from_number:
        return PlainTextResponse("OK")

    whatsapp_handler.handle_message(from_number, incoming_msg)
    return PlainTextResponse("OK")
