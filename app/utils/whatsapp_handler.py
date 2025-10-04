from fastapi import APIRouter
from app.utils.twilio_client import send_whatsapp
from app.services.order_service import OrderProcessor
from models.nlp import NLPModel
from app.utils.pos_machine import PosMachine
from config.configuration_script import user_confirmation, await_confirm, auto_confirm, load_logging


router = APIRouter()

class TwilioWhatsAppHandler:
    def __init__(self):
        self.orderProcessor = OrderProcessor()
        self.nlp_model = NLPModel()
        self.pos_machine = PosMachine()
        self.user_state = {}
        self.user_state_address = {}
        self.CASUAL_RESPONSES = ["ok", "gracias", "dale", "perfecto"]
        self.GREETINGS = ["hola", "hi", "hello", "buenas"]
        self.AWAITING_ORDER = "awaiting_order"
        self.logging = load_logging("logs/tweeliochat.log")
        self.AWAITING_CONFIRMATION = "awaiting_confirmation"

        self.handlers = [
            self.handle_greetings,
            self.handle_menu,
            self.handle_address,
            self.contact_colmadero,
            self.handle_casuals
        ]

    # ---------------- Core Handlers ----------------
    def handle_greetings(self, from_number: str, msg: str) -> bool:
        if msg.lower() in self.GREETINGS:
            send_whatsapp(from_number, "Bienvenido al asistente de pedidos! Escribe 'MENU' o '1' para hacer un pedido.")
            return True
        return False

    def handle_menu(self, from_number: str, msg: str) -> bool:
        if msg == "menu":
            send_whatsapp(from_number, "Menú:\n1 Hacer pedido\n2 Hablar con el colmadero")
            return True
        return False

    def handle_address(self, from_number: str, msg: str) -> bool:
        if msg == "1" and self.user_state.get(from_number) is None:
            send_whatsapp(from_number, "Por favor, introduce tu dirección.")
            self.user_state[from_number] = {"status": "awaiting_address"}
            return True
        return False

    def contact_colmadero(self, from_number: str, msg: str) -> bool:
        if msg == "2":
            send_whatsapp(from_number, "Conectando con el colmadero...")
            return True
        return False

    def handle_casuals(self, from_number: str, msg: str) -> bool:
        if msg in self.CASUAL_RESPONSES:
            send_whatsapp(from_number, "Entendido!")
            return True
        return False

    def display_handlers(self, from_number: str, msg: str) -> bool:
        for handler in self.handlers:
            if handler(from_number, msg):
                return True
        return False

    # ---------------- Order Flow ----------------
    def handle_order(self, from_number: str, msg: str):
        send_whatsapp(from_number, "Cuál es tu pedido?")
        state = self.user_state[from_number]
        state["status"] = self.AWAITING_ORDER
        state["order_lines"] = []
        state["current_index"] = 0

    def ask_confirmation(self, from_number):
        state = self.user_state[from_number]
        line = state["order_lines"][state["current_index"]]

        if len(line["matches"]) == 1:
            line["confirmed"] = line["matches"][0]
            state["current_index"] += 1
            self.ask_next_or_finalize(from_number)
        else:
            msg = f"He encontrado múltiples coincidencias para '{line['original_product']}':\n"
            for i, match in enumerate(line["matches"], 1):
                msg += f"{i}. {match}\n"
            msg += "Por favor responde con el número correcto."
            send_whatsapp(from_number, msg)

    def ask_next_or_finalize(self, from_number):
        state = self.user_state[from_number]
        address = self.user_state_address.get(from_number)
        if state["current_index"] >= len(state["order_lines"]):
            order_lst = [(l["qty"], l["confirmed"]) for l in state["order_lines"]]
            try:
                msg_to_send, total = self.orderProcessor.price_lookup(order_lst)
            except KeyError:
                send_whatsapp(from_number, "Por favor, escribe correctamente los números.")
                return

            send_whatsapp(from_number, msg_to_send)
            send_whatsapp(from_number, f"Precio total: {total}")
            self.orderProcessor.process_order(order_lst, from_number)
            send_whatsapp(from_number, "Pedido finalizado! Escribe 'MENU' para volver al inicio.")
            self.pos_machine.print_fake_receipt(from_number, str(msg_to_send), total, address)
            state["status"] = "order_finished"
        else:
            self.ask_confirmation(from_number)

    # ---------------- Main Entry ----------------
    def handle_message(self, from_number: str, incoming_msg: str):
        from_number = from_number.replace("whatsapp:", "").strip()
        msg = incoming_msg.strip().lower()

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
                send_whatsapp(from_number,
                    "No entendí la cantidad o producto. Por favor, escribe tu pedido usando números '1', '2'; o palabras como 'uno', 'dos'.")
                self.user_state[from_number] = self.AWAITING_ORDER
                send_whatsapp(from_number, "Escribe tu pedido nuevamente:")
                return

            if user_confirmation(from_number, self.user_state, nlp_response, order_lines):
                self.ask_confirmation(from_number)
                return
            else:
                # single match → auto-confirm & process
                auto_confirm(from_number, self.user_state, order_lines, self.orderProcessorer, send_whatsapp)
        # Awaiting confirmation
        await_confirm(from_number, self.user_state, msg, self.ask_next_or_finalize, send_whatsapp)

        # handler options
        if self.display_handlers(from_number, msg):
            return
        # Do not ask for address again
        if self.user_state.get(from_number) == "order_finished":
           return

        # Fallback
        send_whatsapp(from_number,
                                "Si quieres hacer un pedido, escribe 'MENU' o simplemente presiona (1).")
        return