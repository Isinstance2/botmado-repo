from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.services.order_service import process_order
from app.utils.twilio_client import send_whatsapp
from app.services.order_service import OrderProcessor

# Initialize OrderProcessor instance & router
orderProcessor = OrderProcessor()
router = APIRouter()

# In-memory user state tracking
user_state = {}
CASUAL_RESPONSES = ["ok", "gracias", "dale", "perfecto"]

# Key = user phone number, Value = "awaiting_order" or None
user_state = {}

# List of casual responses that shouldn’t trigger an order
CASUAL_RESPONSES = ["ok", "gracias", "dale", "perfecto"]

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        incoming_msg = form.get('Body')
        from_number = form.get('From')
        if from_number:
            from_number = from_number.replace("whatsapp:", "")

        if not incoming_msg or not from_number:
            return PlainTextResponse("OK")

        msg = incoming_msg.strip().lower()

        # 1️Check if user is in "awaiting_order" state first
        if user_state.get(from_number) == "awaiting_order":
            orderProcessor.process_order(incoming_msg, from_number)
            send_whatsapp(from_number, "✅ Pedido recibido! Tu colmado está preparando tu orden.")
            user_state[from_number] = None  # reset state
            return PlainTextResponse("OK")  # stop further processing

        # 2️ Greeting
        if msg in ["hola", "hi", "hello", "buenas", "hey"]:
            send_whatsapp(from_number, "👋 Bienvenido al asistente de pedidos de Colmado! Escribe 'MENU' para ver las opciones o '1' para hacer un pedido.")
            return PlainTextResponse("OK")

        # 3️ Explicit menu trigger
        elif msg == "menu":
            menu_text = (
                "📋 Menú:\n"
                "1️⃣ Hacer pedido\n"
                "2️⃣ Hablar con el colmadero"
            )
            send_whatsapp(from_number, menu_text)
            return PlainTextResponse("OK")

        # 4️Menu options
        elif msg == "1":  # Hacer pedido
            send_whatsapp(from_number, "📩 Cuál es tu pedido?") 
            user_state[from_number] = "awaiting_order"
            return PlainTextResponse("OK")

        elif msg == "2":  # Hablar con colmadero
            send_whatsapp(from_number, "☎️ Conectando con el colmadero...")
            # Optional: call initiate_call(from_number, COLMADERO_NUMBER)
            return PlainTextResponse("OK")

        #  Casual responses
        elif msg in CASUAL_RESPONSES:
            send_whatsapp(from_number, "👌 Entendido! Puedes continuar cuando quieras.")
            return PlainTextResponse("OK")

        # Anything else → guide user
        else:
            send_whatsapp(from_number, "Si quieres hacer un pedido, escribe 'MENU' o simplemente dime qué deseas.")
            return PlainTextResponse("OK")

    except Exception as e:
        print("Error processing webhook:", e)
        return PlainTextResponse("OK")
