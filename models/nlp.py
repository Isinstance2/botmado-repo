import spacy
import random
from spacy.util import minibatch
from data.train_data.nlp_train import TRAIN_DATA
from spacy.training import Example
from config.configuration_script import load_logging, load_env
from database.database_handler import DatabaseHandler
from fuzzywuzzy import process, fuzz
import json
from data.train_data.nlp_train import NUM_MAPPING
dbhandler = DatabaseHandler()
logging = load_logging(logfile="logs/nlp_model_training.log")
import unicodedata




class NLPModel:
    def __init__(self,  model_path="models/customer_order_qty_model"):
        try:
            self.nlp = spacy.load(model_path)
            logging.info(f"Loaded NLP model from {model_path}")
        except Exception as e:
            logging.error(f"Error loading model from {model_path}: {e}")
            self.nlp = spacy.blank("es_core_news_sm")


    @staticmethod
    def normalize_text(s: str) -> str:
        return unicodedata.normalize("NFKC", s).strip().lower().replace("\u200b", "")


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
    
    def get_qty_items(self, entities, text):
        lst = []
        temp_qty = None

        for value, label in entities:
            if label == "QUANTITY":
                temp_qty = value
            elif label in ("PRODUCT", "ITEM") and temp_qty is not None:
                # naive singularization
                if value[-1].lower() == 's':
                    value = value[:-1]
                lst.append((temp_qty, value))
                temp_qty = None

        logging.info(f"Parsed order: {lst} from text: {text}")
        return lst


    def get_order_data(self, orders, detalle_list,score_cutoff=50) -> dict:
        order_lines = []
        for qty, prod in orders:
            qty = (NUM_MAPPING.get(qty, 1) if isinstance(qty, str) else int(qty))
            matched_item = process.extract(prod, detalle_list, limit=20, scorer=fuzz.token_sort_ratio)
            matched_items = [item for item, score in matched_item if score >= score_cutoff]
            order_lines.append({
                "qty": qty,
                "original_product": prod,
                "matches": matched_items if matched_items else [prod],
                "confirmed": None
            })  
                
        return {
            "confirmation_needed": any(len(line['matches']) > 1 for line in order_lines),
            "order_lines" : order_lines
            
        }

    def parse_order(self, text: str):
        clean_msg = " ".join(text.split()).replace("\u200b", "").lower()

        try:
            doc = self.nlp(clean_msg)
            entities = [(ent.text, ent.label_) for ent in doc.ents]

            # Parse quantities and products
            orders = self.get_qty_items(entities, text)

            price_data = dbhandler.extract_collection("price_products") 
            price_lookup = {self.normalize_text(item['DETALLE']): item for item in price_data}  # dict lookup
            detalle_list = list(price_lookup.keys())
        
            order_info = self.get_order_data(orders, detalle_list)
            return order_info

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
            
