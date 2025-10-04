from app.utils import twilio_client
from models.nlp import NLPModel
from app.services.order_service import OrderProcessor
from config.configuration_script import load_logging, user_confirmation, await_confirm, auto_confirm
from app.utils.pos_machine import PosMachine



class WhatsAppSimulator:
    def __init__(self):
        # Initialize core objects
        self.orderProcessor = OrderProcessor()
        self.nlp_model = NLPModel()
        self.pos_machine = PosMachine()
        self.user_state = {}
        self.user_state_address = {}
        self.CASUAL_RESPONSES = ["ok", "gracias", "dale", "perfecto"]
        self.greetings = ["hola", "hi", "hello", "buenas"]
        self.logging = load_logging("logs/simulator.log")
        self.AWAITING_ORDER = "awaiting_order"
        self.AWAITING_CONFIRMATION = "awaiting_confirmation"

        self.handlers = [
            self.handle_greetings,
            self.handle_menu,
            self.handle_address,
            self.contact_colmadero,
            self.handle_casuals
        ]

        # Replace real Twilio send with simulator
        twilio_client.send_whatsapp = self.fake_send_whatsapp

    
     
    def fake_send_whatsapp(self, to: str, message: str):
        """Messaging / Logging"""

        log_msg = f"[WhatsApp -> {to}]: {message}"
        self.logging.info(log_msg)
    

    def handle_greetings(self, from_number: str, msg: str) -> bool:
        
        if msg.lower() in self.greetings:
            self.fake_send_whatsapp(
                from_number,
                "👋 Bienvenido al asistente de pedidos de Colmado! Escribe 'MENU' para ver las opciones o '1' para hacer un pedido."
            )
            return True  # handled
        return False  # not a greeting
    
    def handle_menu(self, from_number: str, msg: str) -> bool:
        if msg == "menu":
                self.fake_send_whatsapp(from_number, 
                                        "📋 Menú:\n" \
                                        "1️⃣ Hacer pedido\n " \
                                        "2️⃣ Hablar con el colmadero")
                return True
        return False
    
    def handle_address(self, from_number: str, msg: str) -> bool:
        if msg == "1" and self.user_state.get(from_number) is None:
            self.fake_send_whatsapp(from_number, "Por favor, Introduce to direccion.")
            self.user_state[from_number] = "awaiting_address"
            return True
        return False

    def handle_order(self, from_number: str, msg: str):
        self.fake_send_whatsapp(from_number, "📩 Cuál es tu pedido?")
        self.user_state[from_number] = self.AWAITING_ORDER
                
    def contact_colmadero(self, from_number: str, msg: str) -> bool:    
        if msg == "2":
                self.fake_send_whatsapp(from_number, "☎️ Conectando con el colmadero...")
                return True
        return False
    
    def handle_casuals(self, from_number: str, msg: str) -> bool:  
        if msg in self.CASUAL_RESPONSES:
                self.fake_send_whatsapp(from_number, "👌 Entendido!")
                return True
        return False
    
    def display_handlers(self, from_number: str, msg: str) -> bool:
        for handler in self.handlers:
            if handler(from_number, msg):
                return True
        return False
    
    def ask_confirmation(self, from_number):

        """Confirmation / Order Flow"""

        state = self.user_state[from_number]
        line = state['order_lines'][state['current_index']]

        if len(line['matches']) == 1:
            line['confirmed'] = line['matches'][0]
            state['current_index'] += 1
            self.ask_next_or_finalize(from_number)
        else:
            msg = f"He encontrado múltiples coincidencias para '{line['original_product']}':\n"
            for i, match in enumerate(line['matches'], 1):
                msg += f"{i}. {match}\n"
            msg += "Por favor responde con el número correcto. si no ves tu producto, escribe 'saltar'."
            self.fake_send_whatsapp(from_number, msg)

    def saltar(self, from_number, msg):
        if msg.lower() == "saltar":
            state = self.user_state[from_number]
            line = state['order_lines'][state['current_index']]
            line['confirmed'] = "Producto no disponible"
            state['current_index'] += 1
            self.ask_next_or_finalize(from_number)
            return True
        return False

    def ask_next_or_finalize(self, from_number):
        state = self.user_state[from_number]
        address = self.user_state_address.get(from_number)
        if state['current_index'] >= len(state['order_lines']):
            # all confirmed → process order
            order_lst = [(l['qty'], l['confirmed']) for l in state['order_lines']]
            try:
                msg_to_send, total = self.orderProcessor.price_lookup(order_lst)
            except KeyError:
                self.fake_send_whatsapp(from_number, "Por favor, escribe correctamente los numeros")

            self.fake_send_whatsapp(from_number, msg_to_send)
            self.fake_send_whatsapp(from_number, f"Precio total: {total}")
            self.orderProcessor.process_order(order_lst, from_number)
            self.fake_send_whatsapp(from_number, "✅ Pedido finalizado! Escribe 'MENU' para volver al inicio.")
            self.pos_machine.print_fake_receipt(from_number, str(msg_to_send), total, address)
            self.user_state[from_number] = "order_finished"
        else:
            # ask next product
            self.ask_confirmation(from_number)

    # Simulator Core Logic
    # -----------------------
    def simulate_message(self, from_number: str, incoming_msg: str):
        from_number = from_number.replace("whatsapp:", "").strip()
        msg = incoming_msg.strip()

        self.logging.info(f"[User -> Bot {from_number}]: {msg}")
        print(f"[User -> Bot {from_number}]: {msg}")

        #order option
        if self.user_state.get(from_number) == "awaiting_address":
            self.user_state_address[from_number] = msg
            self.handle_order(from_number, msg)
            self.logging.info(f"ADDRESS: {self.user_state_address[from_number]}")
            return 
        
            
        
        # Awaiting order
        if self.user_state.get(from_number) == self.AWAITING_ORDER:    
            nlp_response = self.nlp_model.parse_order(msg)
            order_lines = nlp_response.get("order_lines", [])


            if not order_lines:
                self.fake_send_whatsapp(from_number,
                    "No entendí la cantidad o producto. Por favor, escribe tu pedido usando números '1', '2'; o palabras como 'uno', 'dos'.")
                self.user_state[from_number] = self.AWAITING_ORDER
                self.fake_send_whatsapp(from_number, "Escribe tu pedido nuevamente:")
                return

            if user_confirmation(from_number, self.user_state, nlp_response, order_lines):
                self.ask_confirmation(from_number)
                return
            else:
                # single match → auto-confirm & process
                auto_confirm(from_number, self.user_state, order_lines, self.orderProcessor, self.fake_send_whatsapp)
        # Awaiting confirmation
        await_confirm(from_number, self.user_state, msg, self.ask_next_or_finalize, self.fake_send_whatsapp)

        # handler options
        if self.display_handlers(from_number, msg):
            return
        # Do not ask for address again
        if self.user_state.get(from_number) == "order_finished":
           return
        
        if self.saltar(from_number, msg):
            return

        # Fallback
        self.fake_send_whatsapp(from_number,
                                "Si quieres hacer un pedido, escribe 'MENU' o simplemente presiona (1).")
        return
    # Interactive Loop
    def run_interactive_simulation(self):
        print("=== WhatsApp Bot Interactive Simulation ===")
        user_number = input("Enter a test user number (e.g., +18091234567): ").strip()
        print("Type messages to the bot. Type 'exit' to quit.\n")

        while True:
            msg = input("[You -> Bot]: ").strip()
            if msg.lower() == "exit":
                print("Exiting simulation.")
                break
            self.simulate_message(user_number, msg)


# -----------------------
# Run Simulator
# -----------------------
if __name__ == "__main__":
    simulator = WhatsAppSimulator()
    simulator.run_interactive_simulation()
