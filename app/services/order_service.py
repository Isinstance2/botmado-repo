from app.utils.twilio_client import send_whatsapp
from database.database_handler import DatabaseHandler
import random
import string
from datetime import date, datetime
from models.nlp import NLPModel


class OrderProcessor:
    COLMADERO_NUMBER = "whatsapp:+18297531173"

    def __init__(self):
        self.nlpmodel = NLPModel()
        self.dbHandler = DatabaseHandler()
        self.today = date.today().strftime("%Y-%m-%d")

    @staticmethod
    def generate_order_id(length=8) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))

    def process_order(self, message: str, user_number: str) -> str:
        try:
            #  Notify colmadero
            order_text = f"Nuevo pedido de {user_number}: {message}"
            if order_text:
                print("Procesando orden:", order_text)
                try:
                    send_whatsapp(self.COLMADERO_NUMBER, order_text)
                    print(f"Sent order notification to colmadero: {order_text}")
                except Exception as e:
                    print("Twilio send error to colmadero:", e)

                # Confirm to customer
                confirmation = f"✅ Pedido recibido: {message}\nTu colmado está preparando tu orden."
                try:
                    send_whatsapp(user_number, confirmation)
                    print(f"Sent confirmation to customer: {confirmation}")
                except Exception as e:
                    print("Twilio send error to customer:", e)
                
                msg_to_send = self.nlpmodel.parse_order(message)
                if msg_to_send:
                    try:
                        send_whatsapp(user_number, msg_to_send)
                        print(f"Sent NLP response to customer: {msg_to_send}")
                    except Exception as e:
                        print("Twilio send error for NLP response:", e)    

            # Save order to Firebase
            reference_num = self.generate_order_id()
            order_data = {
                'reference_num': reference_num,
                'date': self.today,
                'hora': datetime.now().strftime("%H:%M:%S"),
                'user_number': user_number,
                'message': message,
                'status': 'received'
            }
            try:
                self.dbHandler.save_order(order_data)
                print("Order saved in Firebase:", order_data)
            except Exception as e:
                print("Firebase save error:", e)

        except Exception as e:
            print("Unexpected error in process_order:", e)

        # Twilio webhook expects a response
        return "OK"
