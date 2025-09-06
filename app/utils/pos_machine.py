from escpos.printer import Usb
from config.configuration_script import load_env , load_logging
from datetime import date, datetime
from config.configuration_script import generate_order_id


logging = load_logging(logfile="logs/invoices.log")


class PosMachine:
    def __init__(self, idVendor="place_holder", idProduct="place_holder"):
        self.today = date.today().strftime("%Y-%m-%d")
        self.time =  datetime.now().strftime("%H:%M:%S")

        try:
            self.printer = Usb(idVendor, idProduct)

        except Exception:
            print("⚠️ Using fake printer for development.")
            self.printer = None
        

    def print_text(self, text):
        try:
            self.printer.text(text + "\n")
            self.printer.cut()
            logging.info("Printed text successfully.")
        except Exception as e:
            logging.error(f"Error printing text: {e}")


    def save_invoice(self, from_number, receipt):
        try:
                file_location = f"data/invoices/{from_number}_{self.today}_{self.time}_factura.txt"
                with open(file_location, "w") as f:
                    for text in receipt:
                        f.write(text)
                logging.info(f"receipt has been saved.file location: {file_location}")

        except Exception as e:
            logging.error(f"Couldn't save receipt: {e}")

    def print_fake_receipt(self, from_number, msg_to_send, total, address):
        try:
            reference_num =generate_order_id(length=5)
            
            receipt = (
                "----Colmado Receipt-----\n"
                "------------------------\n"
                f"Codigo: {reference_num}\n"
                f"Fecha: {self.today}\n"
                f"Hora: {self.time}\n"
                ""
                f"{msg_to_send}\n"
                ""
                f"Direccion: {address}\n"
                "------------------------\n"
                f"Total: {total}\n"
            )

            print("FAKE PRINT:",receipt)
            # self.printer.cut()  not used for development yet.

            logging.info("Printed fake receipt successfully.")

            self.save_invoice(from_number, receipt)

        except Exception as e:
            logging.error(f"Error printing fake receipt: {e}")
        