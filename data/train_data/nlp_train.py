import random
import json
TRAIN_DATA_VF = []

TRAIN_DATA_WORD_NUM = []

TRAIN_DATA = [
    ("Quiero 3 galletas y 1 agua", {"entities": [(7, 8, "QUANTITY"), (9, 17, "ITEM"), (20, 21, "QUANTITY"), (22, 26, "ITEM")]}),
    ("Me das 2 jugos y 5 panes", {"entities": [(7, 8, "QUANTITY"), (9, 14, "ITEM"), (17, 18, "QUANTITY"), (19, 24, "ITEM")]}),
    ("Necesito 4 cervezas frías", {"entities": [(10, 11, "QUANTITY"), (12, 20, "ITEM")]}),
    ("Pon 1 chocolate y 2 cafés", {"entities": [(4, 5, "QUANTITY"), (6, 15, "ITEM"), (18, 19, "QUANTITY"), (20, 25, "ITEM")]}),
    ("Dame 6 plátanos", {"entities": [(5, 6, "QUANTITY"), (7, 15, "ITEM")]}),
    ("Tráeme 10 botellas de agua", {"entities": [(7, 9, "QUANTITY"), (10, 24, "ITEM")]}),
    ("Compra 2 pizzas grandes", {"entities": [(7, 8, "QUANTITY"), (9, 14, "ITEM")]}),
    ("Voy a pedir 8 empanadas y 1 refresco", {"entities": [(11, 12, "QUANTITY"), (13, 22, "ITEM"), (25, 26, "QUANTITY"), (27, 35, "ITEM")]}),
    ("Quisiera 3 cafés y 3 donas", {"entities": [(9, 10, "QUANTITY"), (11, 16, "ITEM"), (19, 20, "QUANTITY"), (21, 26, "ITEM")]}),
    ("Regálame 1 sandwich y 2 jugos", {"entities": [(10, 11, "QUANTITY"), (12, 20, "ITEM"), (23, 24, "QUANTITY"), (25, 30, "ITEM")]}),
    ("Ponme 7 manzanas rojas", {"entities": [(6, 7, "QUANTITY"), (8, 16, "ITEM")]}),
    ("Quiero 12 empanadas de pollo", {"entities": [(7, 9, "QUANTITY"), (10, 19, "ITEM")]}),
    ("Dame 4 botellas de vino", {"entities": [(5, 6, "QUANTITY"), (7, 21, "ITEM")]}),
    ("Tráeme 2 hamburguesas dobles", {"entities": [(7, 8, "QUANTITY"), (9, 21, "ITEM")]}),
    ("Voy a comprar 15 huevos", {"entities": [(13, 15, "QUANTITY"), (16, 22, "ITEM")]}),
    ("Me sirven 9 arepas con queso", {"entities": [(10, 11, "QUANTITY"), (12, 18, "ITEM")]}),
    ("Dame 20 naranjas dulces", {"entities": [(5, 7, "QUANTITY"), (8, 16, "ITEM")]}),
    ("Quiero 1 sopa y 2 ensaladas", {"entities": [(7, 8, "QUANTITY"), (9, 13, "ITEM"), (16, 17, "QUANTITY"), (18, 27, "ITEM")]}),
    ("Pon 30 cervezas en la mesa", {"entities": [(4, 6, "QUANTITY"), (7, 15, "ITEM")]}),
    ("Necesito 5 panes integrales", {"entities": [(10, 11, "QUANTITY"), (12, 17, "ITEM")]}),
    ("Tráeme 11 limones", {"entities": [(7, 9, "QUANTITY"), (10, 17, "ITEM")]}),
    ("Quiero 100 caramelos", {"entities": [(7, 10, "QUANTITY"), (11, 20, "ITEM")]}),
    ("Sirve 14 vasos de leche", {"entities": [(6, 8, "QUANTITY"), (9, 22, "ITEM")]}),
    ("Regálame 2 donas de chocolate", {"entities": [(10, 11, "QUANTITY"), (12, 17, "ITEM")]}),
    ("Voy a pedir 6 tacos al pastor", {"entities": [(11, 12, "QUANTITY"), (13, 18, "ITEM")]}),
]

WORDS_NUMBER = [
    "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
    "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve", "treinta",
    "treinta y uno", "treinta y dos", "treinta y tres", "treinta y cuatro", "treinta y cinco", "treinta y seis", "treinta y siete", "treinta y ocho", "treinta y nueve", "cuarenta",
    "cuarenta y uno", "cuarenta y dos", "cuarenta y tres", "cuarenta y cuatro", "cuarenta y cinco", "cuarenta y seis", "cuarenta y siete", "cuarenta y ocho", "cuarenta y nueve", "cincuenta",
    "cincuenta y uno", "cincuenta y dos", "cincuenta y tres", "cincuenta y cuatro", "cincuenta y cinco", "cincuenta y seis", "cincuenta y siete", "cincuenta y ocho", "cincuenta y nueve", "sesenta"
]

NUM_MAPPING = {
    "un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciséis": 16, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiuno": 21, "veintiun": 21, "veintidós": 22, "veintidos": 22,
    "veintitrés": 23, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiséis": 26, "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "treinta y uno": 31, "treinta y dos": 32, "treinta y tres": 33, "treinta y cuatro": 34,
    "treinta y cinco": 35, "treinta y seis": 36, "treinta y siete": 37, "treinta y ocho": 38, "treinta y nueve": 39,
    "cuarenta": 40, "cuarenta y uno": 41, "cuarenta y dos": 42, "cuarenta y tres": 43, "cuarenta y cuatro": 44,
    "cuarenta y cinco": 45, "cuarenta y seis": 46, "cuarenta y siete": 47, "cuarenta y ocho": 48, "cuarenta y nueve": 49,
    "cincuenta": 50, "cincuenta y uno": 51, "cincuenta y dos": 52, "cincuenta y tres": 53, "cincuenta y cuatro": 54,
    "cincuenta y cinco": 55, "cincuenta y seis": 56, "cincuenta y siete": 57, "cincuenta y ocho": 58, "cincuenta y nueve": 59,
    "sesenta": 60, "sesenta y uno": 61
} 

COMPLEMENTARY_PHRASES = ["y", "también", "además", "así como", "junto con", "más", "igualmente", "de igual forma", "de igual manera", ",", "."]

ASKING_PHRASES = ["Quiero", "Me das", "Necesito", "Pon", "Dame", "Tráeme", "Compra", "Voy a pedir", "Quisiera", "Regálame", "Ponme", "Voy a comprar", "Me sirven", "Sirve", "Solicito", "Encarga", "Adquiere", "Consigue", "Provee", "Suministra"]

items = []
with open("data/train_items.txt", "r") as f:
    for item in f:
        items.append(item.strip().lower())
 



for _ in range(2500):  
    qty1 = str(random.randint(1, 60))
    qty1_num = random.choice(WORDS_NUMBER)
    qty2 = str(random.randint(1, 60))
    qty2_num = random.choice(WORDS_NUMBER)

    comp_phrases = str(random.choice(COMPLEMENTARY_PHRASES)) 
    ask_phrase = str(random.choice(ASKING_PHRASES))
    item1 = random.choice(items)
    item2 = random.choice(items)

    # -------- DIGIT VERSION --------
    text = f"{ask_phrase} {qty1} {item1} y {qty2} {item2}"
    start1 = text.find(qty1)
    end1 = start1 + len(qty1)
    start_item1 = text.find(item1, end1)
    end_item1 = start_item1 + len(item1)

    start2 = text.find(qty2, end_item1)
    end2 = start2 + len(qty2)
    start_item2 = text.find(item2, end2)
    end_item2 = start_item2 + len(item2)

    entities_digits = [
        (start1, end1, "QUANTITY"), (start_item1, end_item1, "ITEM"),
        (start2, end2, "QUANTITY"), (start_item2, end_item2, "ITEM")
    ]

    TRAIN_DATA_VF.append((text, {"entities": entities_digits}))

    # -------- WORD VERSION --------
    text_num = f"{ask_phrase} {qty1_num} {item1} {comp_phrases} {qty2_num} {item2}"
    start1_num = text_num.find(qty1_num)
    end1_num = start1_num + len(qty1_num)
    start_item1_num = text_num.find(item1, end1_num)
    end_item1_num = start_item1_num + len(item1)

    start2_num = text_num.find(qty2_num, end_item1_num)
    end2_num = start2_num + len(qty2_num)
    start_item2_num = text_num.find(item2, end2_num)
    end_item2_num = start_item2_num + len(item2)

    entities_words = [
        (start1_num, end1_num, "QUANTITY"), (start_item1_num, end_item1_num, "ITEM"),
        (start2_num, end2_num, "QUANTITY"), (start_item2_num, end_item2_num, "ITEM")
    ]

    TRAIN_DATA_WORD_NUM.append((text_num, {"entities": entities_words}))

with open("data/train_data/model_training_data.json", "w") as f:
    json.dump(TRAIN_DATA + TRAIN_DATA_VF + TRAIN_DATA_WORD_NUM, f, ensure_ascii=False, indent=2)