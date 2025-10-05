# WhatsApp Order Assistant — Conversational Ordering System

Customers can place and confirm store orders directly through WhatsApp thanks to the clever conversational system known as WhatsApp Order Assistant.
It combines NLP-based order parsing, Twilio, and FastAPI to mimic a real-time shopping assistant that can comprehend natural language order inputs, control order flows, and communicate with a mock Point of Sale (POS) system.

## Table of Contents

- [Features](#features)
- [Techstack](#techstack)
- [Conversation Flow](#conversation-flow)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Future Work](#future-work)
- [License](#License)


## Features

* WhatsApp Integration (Twilio Sandbox): Users and the assistant can communicate in real time.
* Dynamic Conversation Flow: Manages order confirmation, address collection, menu selection, greetings, and the creation of the final receipt.
* In order to preserve a consistent conversation context, state management keeps track of each user's progress (awaiting_address, awaiting_order, awaiting_confirmation, etc.).
* Natural language product orders, such as "2 jugos y un pan," are processed by NLP order parsing, which also recognizes product names and quantities.
* For testing and presentation purposes, POS Simulation creates and prints a phony digital receipt.
* Firebase Connectivity (Optional) – Can be configured to save orders directly to Firebase for real-time storage and retrieval, enabling persistence across sessions.

## Techstack
* **Backend:** Python + FastAPI
* **Messaging API:** Twilio WhatsApp Sandbox
* **Order Parsing:** NLP-based product recognition
* **Utilities:** POS simulator (PosMachine), Twilio client wrapper, confirmation services
* **Environment Management:** dotenv for secure local configuration


Conversation Flow

Greeting – User says “hola”, “hi”, or similar → bot responds with menu options.

Menu – Options:

1 – Place an order

2 – Contact colmadero (shop owner)

3 - Address – If 1, bot asks for the delivery address.

4 - Order Input – User types products and quantities in natural language.

5 - Confirmation – For ambiguous products, bot lists matches and asks for selection.

6 - Order Finalization – Once all products are confirmed:

   * Bot calculates total price.
   * Sends order summary.
   * Generates a POS-style receipt.
   * Optionally saves to Firebase.

## Installation

```
# Clone the repository
git clone https://github.com/yourusername/colmado_ai.git
cd colmado_ai

# Create a virtual environment
python -m venv colai_env
source colai_env/bin/activate  # Linux/macOS
colai_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

```

* Configure .env with the following keys:
```
FB_K=path/to/firebase-adminsdk.json
TWILIO_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890
PROD_PRECIOS=path/to/prod_precios.csv
INVOICES_DIR=invoices
```
* Optional: Install ngrok for exposing your local server to Twilio:

```
ngrok http 8000
```

## Usage

1. Simulator (Local Testing)

```
python simulate_bot_grok.py

```
2. Twilio Integration

Run FastAPI server:

```
uvicorn app.main:app --reload
```

* Expose server to the internet with ngrok.
* Configure Twilio webhook to point to /whatsapp endpoint on the ngrok URL.
* Start messaging your WhatsApp bot.



## Project Structure

```

colmado_ai/
├── app/
│   ├── api/
│   │   └── order_routes.py          # FastAPI routes for Twilio webhooks
│   ├── main.py                      # FastAPI main app
│   ├── services/
│   │   └── order_service.py         # Order processing logic
│   └── utils/
│       ├── twilio_client.py         # Twilio messaging utility
│       ├── pos_machine.py           # POS receipt simulation
│       └── whatsapp_handler.py      # Core bot logic
├── config/
│   └── configuration_script.py      # Config and helper functions
├── data/
│   ├── price_products.csv           # Product price data
│   ├── prod_precios.csv             # Sample product prices
│   ├── invoices/                    # Folder to store order invoices
│   └── config_data/
│       └── colmado-ai-firebase-adminsdk.json
├── database/
│   └── database_handler.py          # Firebase / DB interactions
├── models/
│   ├── nlp.py                       # NLP parser for order input
│   └── customer_order_qty_model/    # Optional NLP model for quantity parsing
├── simulate_bot_grok.py             # Local conversation simulation
├── logs/                             # Log files for debugging and orders
├── requirements.txt
├── setup.py
└── .env
```


## Future Work

* Add AI-powered suggestions for product recommendations.
* Integrate user profiles for repeat orders and history tracking.
* Expand multi-language support for NLP parsing.
* Implement real-time inventory checks via Firebase.

## License
This project is for personal and educational use only. All rights reserved.




