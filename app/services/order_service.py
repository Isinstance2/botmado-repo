from app.utils.twilio_client import send_whatsapp
from database.database_handler import DatabaseHandler
import random
import string
from datetime import date, datetime
from models.nlp import NLPModel
from fuzzywuzzy import process
from data.train_data.nlp_train import NUM_MAPPING

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
                

            # Save order to Firebase
            reference_num = self.generate_order_id()
            order_data = {
                'reference_num': reference_num,
                'date': self.today,
                'hora': datetime.now().strftime("%H:%M:%S"),
                'user_number': user_number,
                'message': "; ".join(f"{qty} {product}" for qty, product in message),
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
    
    def price_lookup(self, lst: list):
        msg_to_send = ""
        updated_order = []

        price_data = self.dbHandler.extract_collection("price_products")
        price_lookup = {item['DETALLE'].strip().lower(): item for item in price_data}
        detalle_list = list(price_lookup.keys())  

        for qty, prod in lst:
            qty = NUM_MAPPING.get(qty, 1) if isinstance(qty, str) else int(qty)

            # Fuzzy match
            match_item = process.extractOne(prod, detalle_list, score_cutoff=70)
            if not match_item:
                match_item = ["Producto desconocido"]

            price_info = price_lookup.get(match_item[0])
            prod_price = float(price_info['COSTO']) if price_info else 0

            updated_order.append({
                "qty": qty,
                "product": prod,
                "price": prod_price
            })

            # Add to message immediately
            total_item_price = qty * prod_price
            if prod_price > 0:
                msg_to_send += f"{qty} x {match_item[0]} = ${total_item_price:.2f}\n"
            else:
                msg_to_send += f"{qty} x {prod} | Precio no disponible\n"

        # Sum all prices
        all_prices = sum(item["price"] * item["qty"] for item in updated_order)

        return msg_to_send, all_prices

