from dotenv import load_dotenv
import os

load_dotenv() # loads environment variables from the .env file
# telegram settings used to send push notifications to a chat
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") # stores the telegram bot token
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") # stores the target telegram chat id


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///FlatWatch.db") # default sqlite path used when no database url is set


FILTERS = {
"miasto": "Krakow", # main city used for the olx and otodom search urls
"typ": "wynajem", # listing type, such as rental or sale
"cena_min": 0, # minimum price in pln
"cena_max": 500000, # maximum price in pln

"powierzchnia_min": 0, # minimum area in square meters
"powierzchnia_max": 1000, # maximum area in square meters

"tylko_prywatne": True, # keeps only private offers when enabled
}

SERVICES = { # websites that are active in the scraping flow
    "olx" : True,
    "otodom" : True
}

OLX_CATEGORY_ID = 15 # apartment category id used by olx

OLX_REGIONS = { # region ids used for olx queries
    "Krakow" : 4,
    "Warszawa" : 7,
    "Wroclaw" : 9,

}
OLX_CITIES = { # city ids used for olx queries
    "Krakow": "8959",
}

CITY_NORMALIZED = { # normalizes city names to keep filtering consistent
    "krakow": "kraków",
    "warszawa": "warszawa",
    "wroclaw": "wrocław",
    "gdansk": "gdańsk",
    "poznan": "poznań",
    "lodz": "łódź",
    "katowice": "katowice",
}

OTODOM_CITIES = {
    "krakow": "malopolskie/krakow/krakow/krakow",
    "warszawa": "mazowieckie/warszawa/warszawa/warszawa",
    "wroclaw": "dolnoslaskie/wroclaw/wroclaw/wroclaw",
    "gdansk": "pomorskie/gdansk/gdansk/gdansk",
    "poznan": "wielkopolskie/poznan/poznan/poznan",
    "lodz": "lodzkie/lodz/lodz/lodz",
    "katowice": "slaskie/katowice/katowice/katowice",
}

INTERVAL_MINUTES = 30 # how often the app checks for new offers in minutes