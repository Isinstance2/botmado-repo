import ollama
import json
from config.configuration_script import load_logging

logging = load_logging()

class AiCompanion():
    def __init__(self):
         
        self.system_prompt = """
            Eres un asistente experto en gestión de colmados y ventas minoristas. 
                Tu tarea es ayudar a manejar órdenes de clientes, controlar inventario y organizar pedidos de manera clara y eficiente. 

                Funciones principales:
                1. Registrar pedidos con productos, cantidades y precios.
                2. Consultar inventario y verificar disponibilidad de productos.
                3. Sugerir productos complementarios si aplica.
                4. Generar resúmenes de pedidos listos para cobrar.
                5. Detectar errores comunes en pedidos y avisar.

                Tono:
                - Profesional pero cercano.
                - Conciso y claro.
                - Evita inventar productos o información fuera del contexto.
                """

    def call_assistant(self):
        try:
            logging.debug("Initializing . . .")
            self.response = ollama.chat(
                model="llama3",
                messages=[
                {"role": "system", "content": self.system_prompt.strip()},
                {"role": "user", "content": self.user_prompt.strip()}
                ]
                )
            logging.info("Agent has been initiated.")
            return str(self.response['message']['content'])
        except Exception as e:
            logging.error(f"Couldn't initialize AI agent : {e}")