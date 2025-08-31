import logging
from app.utils import twilio_client
from models.nlp import NLPModel
from app.services.order_service import OrderProcessor

orderProcessor = OrderProcessor()

# 1️⃣ Logging setup (Grok can read this file)
logging.basicConfig(
    filename="simulation.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# 2️⃣ Replace real send_whatsapp with a fake one for simulation
def fake_send_whatsapp(to: str, message: str):
    log_msg = f"[WhatsApp -> {to}]: {message}"
    logging.info(log_msg)
    print(log_msg)

twilio_client.send_whatsapp = fake_send_whatsapp

# 3️⃣ In-memory user state
user_state = {}

# 4️⃣ Casual responses
CASUAL_RESPONSES = ["ok", "gracias", "dale", "perfecto"]

# 5️⃣ Simulate webhook logic
def simulate_message(from_number: str, incoming_msg: str):
    from_number = from_number.replace("whatsapp:", "").strip()
    msg = incoming_msg.strip()


    logging.info(f"[User -> Bot {from_number}]: {msg}")
    print(f"[User -> Bot {from_number}]: {msg}")

    # Check if user is awaiting an order
    if user_state.get(from_number) == "awaiting_order":
        nlp_msg = incoming_msg.encode("utf-8").decode("utf-8")
        nlp_msg = " ".join(nlp_msg.split())
        orderProcessor.process_order(nlp_msg, from_number)
        fake_send_whatsapp(from_number, "✅ Pedido recibido! Tu colmado está preparando tu orden.")
        user_state[from_number] = None
        return

    # Greeting
    if msg in ["hola", "hi", "hello", "buenas"]:
        fake_send_whatsapp(from_number, "👋 Bienvenido al asistente de pedidos de Colmado! Escribe 'MENU' para ver las opciones o '1' para hacer un pedido.")
        return

    # Menu trigger
    if msg == "menu":
        fake_send_whatsapp(from_number, "📋 Menú:\n1️⃣ Hacer pedido\n2️⃣ Hablar con el colmadero")
        return

    # Menu options
    if msg == "1":
        fake_send_whatsapp(from_number, "📩 Cuál es tu pedido?")
        user_state[from_number] = "awaiting_order"
        return

    if msg == "2":
        fake_send_whatsapp(from_number, "☎️ Conectando con el colmadero...")
        return

    # Casual responses
    if msg in CASUAL_RESPONSES:
        fake_send_whatsapp(from_number, "👌 Entendido! Puedes continuar cuando quieras.")
        return

    # Fallback
    fake_send_whatsapp(from_number, "Si quieres hacer un pedido, escribe 'MENU' o simplemente dime qué deseas.")
    return

# Interactive loop for testing
def run_interactive_simulation():
    
    print("=== WhatsApp Bot Interactive Simulation ===")
    user_number = input("Enter a test user number (e.g., +18091234567): ").strip()
    print("Type messages to the bot. Type 'exit' to quit.\n")

    while True:
        msg = input("[You -> Bot]: ").strip()
        if msg.lower() == "exit":
            print("Exiting simulation.")
            break
        simulate_message(user_number, msg)

if __name__ == "__main__":
    run_interactive_simulation()


