import pandas as pd
from config.configuration_script import load_env , load_logging
import firebase_admin
from firebase_admin import credentials, firestore
import os




class DatabaseHandler:
    def __init__(self):
        self.logging = load_logging()
        self.FB_K = os.getenv("FB_K")

        if not self.FB_K:
            self.logging.warning("FB_K is missing!")

        self.cred =  credentials.Certificate(self.FB_K)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(self.cred)

        self.db = firestore.client()
        self.logging.info("Firebase connection initialized.")

        price_database = pd.read_csv("data/prod_precios.csv")
        self.price_db = price_database.to_dict(orient="records")


    def extract_collection(self, collection_name, local_db=True):
        """Extract a Firestore collection"""

        if local_db:
            data = [
                {**doc, "id": idx}  # Add a fake ID to match Firestore structure
                for idx, doc in enumerate(self.price_db)
            ]
            self.logging.info(f"Extracted {len(data)} docs from local DB '{collection_name}'.")
            return data

        else:

            try:
                
                docs = self.db.collection(collection_name).stream()  # fetch docs
                data = [
                    {**doc.to_dict(), "id": doc.id}
                    for doc in docs
                ]
                self.logging.info(f"Extracted {len(data)} docs from '{collection_name}'.")
                return data
            except Exception as e:
                self.logging.error(f"Error extracting collection '{collection_name}': {e}")
                return [] 
              
    def save_order(self, order_data: dict, collection_name='orders'):
        """Save an order to the 'orders' collection."""
        try:
            orders_ref = self.db.collection(collection_name)    
            orders_ref.add(order_data)
            self.logging.info("Order saved successfully.")
        except Exception as e:
            self.logging.error(f"Error saving order: {e}")

    def read_collection(self, collection_name):
        """Read all documents from a Firestore collection."""
        try:
            docs = self.db.collection(collection_name).stream()
            data = [doc.to_dict() for doc in docs]
            self.df = pd.DataFrame(data)
            self.df = self.df[['Product', 'Stock', 'Price']]
            self.df = self.df.iloc[:-1, :]  # Drop the last column if exists
            self.logging.info(f"Read {len(self.df)} documents from collection '{collection_name}'.")
            return self.df
        except Exception as e:
            self.logging.error(f"Error reading collection '{collection_name}': {e}")
            return pd.DataFrame()
        
    def save_to_collection(self, collection_name, data: pd.DataFrame):
        try:
            collection_ref = self.db.collection(collection_name)
            for index, row in data.iterrows():
                doc_id = str(index)  # or use row["Product"] for unique ID
                collection_ref.document(doc_id).set(row.to_dict())
            self.logging.info(f"Data saved to collection '{collection_name}'.")
        except Exception as e:
            self.logging.error(f"Error saving data to collection '{collection_name}': {e}")



if __name__ == "__main__":
    db_handler = DatabaseHandler()
    df = db_handler.read_collection("stock")
    print(df)