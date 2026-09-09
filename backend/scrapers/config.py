from dotenv import load_dotenv
import os

load_dotenv() # wczytuje zmienne z .env
# Tokeny uzywane do wysylania powiadomien na telefon
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


DATABASE_URL = os.getenv("DATABASE_URL") # adres bazy Postgres, lokalnie z .env, w Actions z sekretow


FILTERS = {
"miasto": "Krakow", # miasto do url olx/otodom
"typ": "sprzedaz", # sprzedaz/wynajem
"cena_min": 0,
"cena_max": 450000, # max/min cena w PLN

"powierzchnia_min": 30,
"powierzchnia_max": 1000, # max/min powierzchnia w m2

"zabudowa": ["blok", "apartamentowiec"], # blok/apartamentowiec/kamienica/pozostale, pusta lista to wszystkie

"tylko_prywatne": False, #tylko ogloszenia prywtane bez posrednikow w przypadku True
}

SERVICES = { # Strony z ktorych bedziemy korzystac
    "olx" : True
}

OLX_CATEGORIES = {
    "sprzedaz": 14,
    "wynajem": 15,
}

OLX_BUILDTYPES = ("blok", "apartamentowiec", "kamienica", "pozostale")

OLX_REGIONS = { # id regionu
    "krakow" : 4,
    "warszawa" : 7,
    "wroclaw" : 9,

}
OLX_CITIES = { # id miasta
    "krakow": "8959",
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