from escpos.printer import Usb
from config.configuration_script import load_env , load_logging

logging = load_logging()


class PosMachine:
    def __init__(self, idVendor, idProduct):
        self.printer = Usb(idVendor, idProduct)

    def print_text(self, text):
        try:
            self.printer.text(text + "\n")
            self.printer.cut()
            logging.info("Printed text successfully.")
        except Exception as e:
            logging.error(f"Error printing text: {e}")

    def print_fake_receipt(self):
        try:
            self.printer.text("Colmado Receipt\n")
            self.printer.text("------------------------\n")
            self.printer.text("Item 1       $10.00\n")
            self.printer.text("Item 2       $15.00\n")
            self.printer.text("------------------------\n")
            self.printer.text("Total        $25.00\n")
            self.printer.cut()
            logging.info("Printed fake receipt successfully.")
        except Exception as e:
            logging.error(f"Error printing fake receipt: {e}")
        