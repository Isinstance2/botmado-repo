import spacy
import random
from spacy.util import minibatch
from data.train_data.nlp_train import TRAIN_DATA
from spacy.training import Example
from config.configuration_script import load_logging, load_env
from database.database_handler import DatabaseHandler
from fuzzywuzzy import process
import json
from data.train_data.nlp_train import NUM_MAPPING
dbhandler = DatabaseHandler()
logging = load_logging(logfile="logs/nlp_model_training.log")




class NLPModel:
    def __init__(self,  model_path="models/customer_order_qty_model"):
        try:
            self.nlp = spacy.load(model_path)
            logging.info(f"Loaded NLP model from {model_path}")
        except Exception as e:
            logging.error(f"Error loading model from {model_path}: {e}")
            self.nlp = spacy.blank("es_core_news_sm")


    def train_ner_model(self, model_path="models/customer_order_qty_model", TRAIN_DATA=TRAIN_DATA):
        try:
            if 'ner' not in self.nlp.pipe_names:
                ner = self.nlp.add_pipe("ner")
            else:
                ner = self.nlp.get_pipe("ner")

            for _, annotations in TRAIN_DATA:
                for ent in annotations.get("entities"):
                    if ent[2] not in ner.labels:
                        ner.add_label(ent[2])

            other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
            with self.nlp.disable_pipes(*other_pipes):
                optimizer = self.nlp.begin_training()
                
                epochs = 50
                for epoch in range(epochs):
                    random.shuffle(TRAIN_DATA)
                    losses = {}
                    batches = minibatch(TRAIN_DATA, size=8)
                    for batch in batches:
                        examples = []
                        for text, annotations in batch:
                            doc = self.nlp.make_doc(text)
                            example = Example.from_dict(doc, annotations)
                            examples.append(example)
                        self.nlp.update(examples, sgd=optimizer, drop=0.3, losses=losses)
                    print(f"Epoch {epoch + 1}/{epochs}, Losses: {losses}")
                    
            self.nlp.to_disk(model_path)
            logging.info("Model saved to models/customer_order_qty_model")
        except Exception as e:
            logging.error(f"Error during model training: {e}")

    @staticmethod
    def load_trained_model(model_path="models/customer_order_qty_model"):
        trained_nlp = spacy.load(model_path)
        return trained_nlp
    
    def parse_order(self, text: str):
        orders = []
        temp_qty = None
        msg_to_send = ""

        clean_msg = " ".join(text.split()).replace("\u200b", "").lower()

        try:
            doc = self.nlp(clean_msg)
            entities = [(ent.text, ent.label_) for ent in doc.ents]

            # Parse quantities and products
            for value, label in entities:
                if label == "QUANTITY":
                    temp_qty = value
                elif label in ("PRODUCT", "ITEM") and temp_qty is not None:
                    # naive singularization
                    if value[-1].lower() == 's':
                        value = value[:-1]
                    orders.append((temp_qty, value))
                    temp_qty = None

            logging.info(f"Parsed order: {orders} from text: {text}")

            price_data = dbhandler.extract_collection("price_products")
            price_lookup = {item['DETALLE'].strip().lower(): item for item in price_data}  # dict for O(1) lookup
            detalle_list = list(price_lookup.keys())

            for qty, prod in orders:
                qty = (NUM_MAPPING.get(qty, 1) if isinstance(qty, str) else int(qty))
                matched_item = process.extractOne(prod, detalle_list, limit=5, score_cutoff=70)
                if matched_item:
                    price = price_lookup.get(matched_item[0])
                    if price:
                        logging.info(f"Matched '{prod}' to '{matched_item[0]}' with price {price['COSTO']}")    
                        total_item_price = qty * float(price['COSTO'])
                        msg_to_send += f"{qty} x {matched_item[0]} - ${total_item_price:.2f}\n"
                        print(msg_to_send, flush=True)
                else:
                    logging.warning(f"No match found for product '{prod}'")
                    msg_to_send += f"{qty} x {prod} - Precio no disponible\n"

            return matched_item, msg_to_send if msg_to_send else None

        except Exception as e:
            logging.error(f"Error parsing order from text '{text}': {e}")

        



            
            
            



if __name__ == "__main__":
    with open("data/train_data/model_training_data.json", "r") as f:
        TRAIN_DATA_VF = json.load(f)


    nlp_model = NLPModel()
    nlp_model.train_ner_model(TRAIN_DATA=TRAIN_DATA_VF)
    trained_nlp = nlp_model.load_trained_model()
    test_texts = [
        "1 agua y dos galleta",
        "Envía 12 latas de refresco a la tienda.",
        "Necesitamos 7 cajas de galletas para la fiesta."
    ]

    for text in test_texts:
        doc = trained_nlp(text)
        print(f"\nText: {text}")
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print()
            
