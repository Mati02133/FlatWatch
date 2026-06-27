from dotenv import load_dotenv
import os

load_dotenv() # wczytuje zmienne z .env
# Tokeny uzywane do wysylania powiadomien na telefon
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///flatwatch.db")


FILTERS = {
"miasto": "Krakow", # miasto do url olx/otodom
"typ": "wynajem", # sprzedaz/wynajem
"cena_min": 0,
"cena_max": 500000, # max/min cena w PLN

"powierzchnia_min": 0,
"powierzchnia_max": 1000, # max/min powierzchnia w m2

"tylko_prywatne": True, #tylko ogloszenia prywtane bez posrednikow w przypadku True
}

SERVICES = { # Strony z ktorych bedziemy korzystac
    "olx" : True,
    "otodom" : True
}

