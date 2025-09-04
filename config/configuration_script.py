from dotenv import load_dotenv
import os
import logging



def load_logging(logfile="colmado_ai.log", level=logging.INFO):
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
    

""" SIMULATOR CORE LOGIC HELPER"""

def user_confirmation(from_number, user_state, nlp_response, order_lines, status="awaiting_confirmation") -> bool:
    if nlp_response.get("confirmation_needed"):
        user_state[from_number] = {
            "status": status,
            "order_lines": order_lines,
            "current_index": 0
        }
        
        return True
    return False