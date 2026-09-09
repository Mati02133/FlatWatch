from dotenv import load_dotenv
import os

load_dotenv() # wczytuje zmienne z .env
# Tokeny uzywane do wysylania powiadomien na telefon
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


DATABASE_URL = os.getenv("DATABASE_URL") # adres bazy Postgres, lokalnie z .env, w Actions z sekretow


FILTERS = {
"miasto": "Krakow", # miasto do url olx/otodom
"typ": "wynajem", # sprzedaz/wynajem
"cena_min": 2090,
"cena_max": 2090, # max/min cena w PLN

"powierzchnia_min": 0,
"powierzchnia_max": 1000, # max/min powierzchnia w m2

"tylko_prywatne": False, #tylko ogloszenia prywtane bez posrednikow w przypadku True
}

SERVICES = { # Strony z ktorych bedziemy korzystac
    "olx" : True
}

OLX_CATEGORY_ID = 15 # 15 to mieszkania

OLX_REGIONS = { # id regionu
    "Krakow" : 4,
    "Warszawa" : 7,
    "Wroclaw" : 9,

}
OLX_CITIES = { # id miasta
    "Krakow": "8959",
}

CITY_NORMALIZED = {
    "krakow": "kraków",
    "warszawa": "warszawa",
    "wroclaw": "wrocław",
    "gdansk": "gdańsk",
    "poznan": "poznań",
    "lodz": "łódź",
    "katowice": "katowice",
}

INTERVAL_MINUTES = 30 # co ile minut bedzie sprawdzac nowe ogloszenia