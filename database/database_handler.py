import pandas as pd
from config.configuration_script import load_env , load_logging
import firebase_admin
from firebase_admin import credentials, firestore



FB_K = load_env(".env", "FB_K")


class DatabaseHandler:
    def __init__(self):
        self.cred =  credentials.Certificate(FB_K)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(self.cred)

        self.db = firestore.client()
        self.logging = load_logging()
        self.logging.info("Firebase connection initialized.")

    def extract_collection(self, collection_name):
        """Extract a Firestore collection"""
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