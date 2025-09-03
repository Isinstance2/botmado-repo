import logging
from app.utils import twilio_client
from models.nlp import NLPModel
from app.services.order_service import OrderProcessor

orderProcessor = OrderProcessor()
nlp_model = NLPModel()

#  Logging setup (Grok can read this file)
logging.basicConfig(
    filename="simulation.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def ask_confirmation(from_number):
    state = user_state[from_number]
    line =  state['order_lines'][state['current_index']]

    if len(line['matches']) == 1:
        line['confirmed'] = line['matches'][0]
        state['current_index'] += 1
        ask_next_or_finalize(from_number)

    else:
        msg = f"He encontrado múltiples coincidencias para '{line['original_product']}':\n"
        for i, match in enumerate(line['matches'], 1):
            msg += f"{i}. {match}\n"
        msg += "Por favor responde con el número correcto."
        fake_send_whatsapp(from_number, msg)

def ask_next_or_finalize(from_number):
    state = user_state[from_number]
    if state['current_index'] >= len(state['order_lines']):
        # all confirmed → process order
        order_lst = [(l['qty'], l['confirmed']) for l in state['order_lines']]
        try:
            msg_to_send, total = orderProcessor.price_lookup(order_lst)

        except KeyError:
            fake_send_whatsapp(from_number, "Por favor, escribe correctamente los numeros")
        fake_send_whatsapp(from_number, msg_to_send)
        fake_send_whatsapp(from_number, f"Precio total: {total}")
        orderProcessor.process_order(order_lst, from_number)
        user_state[from_number] = None
    else:
        # ask next product
        ask_confirmation(from_number)



#  Replace real send_whatsapp with a fake one for simulation
def fake_send_whatsapp(to: str, message: str):
    log_msg = f"[WhatsApp -> {to}]: {message}"
    logging.info(log_msg)
    

twilio_client.send_whatsapp = fake_send_whatsapp

#  In-memory user state
user_state = {}

# Casual responses
CASUAL_RESPONSES = ["ok", "gracias", "dale", "perfecto"]

#  Simulate webhook logic
def simulate_message(from_number: str, incoming_msg: str):
    from_number = from_number.replace("whatsapp:", "").strip()
    msg = incoming_msg.strip()


    logging.info(f"[User -> Bot {from_number}]: {msg}")
    print(f"[User -> Bot {from_number}]: {msg}")

    # Check if user is awaiting an order
    if user_state.get(from_number) == "awaiting_order":
        nlp_response = nlp_model.parse_order(msg)

        order_lines = nlp_response.get("order_lines", [])

        if not order_lines:
        # No valid order detected → ask user to repeat
            fake_send_whatsapp(from_number, "No entendí la cantidad o producto. Por favor, escribe tu pedido usando números o palabras como 'un', 'dos'.")
            user_state[from_number] = "awaiting_order"
            fake_send_whatsapp(from_number, "Escribe tu pedido nuevamente:") 
            return

        if nlp_response.get("confirmation_needed"):
            # Then store state
            user_state[from_number] = {
                "status": "awaiting_confirmation",
                "order_lines": order_lines,
                "current_index": 0
            }
            ask_confirmation(from_number)
            return
    
        else:
        # single match → auto-confirm & process
            order_lst = [(line['qty'], line['matches'][0]) for line in order_lines]
            msg_to_send, total = orderProcessor.price_lookup(order_lst)
            fake_send_whatsapp(from_number, msg_to_send)
            fake_send_whatsapp(from_number, f"Precio total: {total}")
            orderProcessor.process_order(order_lst, from_number)
            user_state[from_number] = None
            

    if isinstance(user_state.get(from_number), dict) and user_state[from_number].get('status') == "awaiting_confirmation":
        state = user_state[from_number]
        line = state['order_lines'][state['current_index']]

        # user replies with number
        try:
            selected_index = int(msg.strip()) - 1

        
            line['confirmed'] = line['matches'][selected_index]
            state['current_index'] += 1

            ask_next_or_finalize(from_number)
        except ValueError:
            fake_send_whatsapp(from_number, "Por favor, responde solo con el número correspondiente a tu elección.")
        
        except IndexError:
            fake_send_whatsapp(from_number, "Ese número no corresponde a ninguna opción. Intenta de nuevo.")
           






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
    fake_send_whatsapp(from_number, "Si quieres hacer un pedido, escribe 'MENU' o simplemente presiona (1).")
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


