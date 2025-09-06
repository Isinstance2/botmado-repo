from dotenv import load_dotenv
import os
import logging
import random
import string




def load_logging(logfile="colmado_ai.log", level=logging.INFO):
    """Load logger"""
    logger = logging.getLogger()  # ✅ Don't shadow the module name
    logger.setLevel(level)

    # Remove all handlers (prevents duplicates)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # File Handler
    file_handler = logging.FileHandler(logfile, mode='a')
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    ))

    logger.addHandler(console_handler)

    return logger



def load_env(env_path:str, variable_name:str):
    """Load environment variables from a .env file."""
    try:
        load_dotenv(env_path)
        env_variable = os.getenv(variable_name)
        return env_variable if env_variable else None
    except Exception as e:
        logging.error(f"Error loading environment variable '{variable_name}': {e}")
        return None
    

def generate_order_id(length=8) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))
    

"""CORE LOGIC HELPER"""

def user_confirmation(from_number, user_state, nlp_response, order_lines, status="awaiting_confirmation") -> bool:
    if nlp_response.get("confirmation_needed"):
        user_state[from_number] = {
            "status": status,
            "order_lines": order_lines,
            "current_index": 0
              
        }
        
        return True
    return False

def auto_confirm(from_number,user_state,order_lines, orderProcessor, send_msg_func):
     order_lst = [(line['qty'], line['matches'][0]) for line in order_lines if line['matches']]
     msg_to_send, total = orderProcessor.price_lookup(order_lst)
     send_msg_func(from_number, msg_to_send)
     send_msg_func(from_number, f"Precio total: {total}")
     orderProcessor.process_order(order_lst, from_number)
     user_state[from_number] = None


def await_confirm(from_number, user_state, msg, ask_next_func, send_msg_func):
     if isinstance(user_state.get(from_number), dict) and \
           user_state[from_number].get('status') == "awaiting_confirmation":
           state = user_state[from_number]
           line = state['order_lines'][state['current_index']]
           try:
                selected_index = int(msg.strip()) - 1
                line['confirmed'] = line['matches'][selected_index]
                state['current_index'] += 1
                ask_next_func(from_number)

                if user_state.get(from_number) is None:
                     return
           except ValueError:  
                send_msg_func(from_number,
                                    "Por favor, responde solo con el número correspondiente a tu elección.")
           except IndexError:
                send_msg_func(from_number,
                                    "Ese número no corresponde a ninguna opción. Intenta de nuevo.")

                
