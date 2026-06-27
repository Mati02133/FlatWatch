import requests
from bs4 import BeautifulSoup
from config import OLX_CATEGORY_ID, OLX_REGIONS, FILTERS, OLX_CITIES


BASE_URL = "https://www.olx.pl/api/v1/offers/" # API do pobierania ogloszen

def build_params() -> dict:
    city = FILTERS["miasto"].lower()
    region_id = OLX_REGIONS.get(city, 4) # domyslnie Krakow jak nie ma miasta
    city_id = OLX_CITIES.get(city)

    params =  {
        "category_id": OLX_CATEGORY_ID,
        "region_id": region_id,
        "limit": 50, # ilosc ogloszen do pobrania w jednym momencie
        "offset": 0, # od jakiego indeksu zaczynamy
        "sort_by": "created_at:desc", # sortowanie
    }
    
    # Dodatkowe warunki, ktory mozna podac ale nie trzeba
    if city_id:
            params["city_id"] = city_id
    if FILTERS.get("cena_min"):
        params["filter_float_price:from"] = FILTERS["cena_min"]
    
    if FILTERS.get("cena_max"):
        params["filter_float_price:to"] = FILTERS["cena_max"]
    
    if FILTERS.get("powierzchnia_min"):
        params["filter_float_m:from"] = FILTERS["powierzchnia_min"]
    
    if FILTERS.get("powierzchnia_max"):
        params["filter_float_m:to"] = FILTERS["powierzchnia_max"]
    
    return params

def decode_html(html) -> str: # dekoduje html do czystego tekstu
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def get_price(params_list) ->  list:
    for params in params_list:
        if params.get("key") == "price": 
            return params["value"].get("value")
        return None

def fetch_offers() -> list:
    params = build_params()
    headers = { # headers uzywamy po to aby nie zostac zablokowanym przez serwer imitujac przegladarke
        "User-Agent": "Mozilla/5.0 (compatible; FlatWatch/1.0)",
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=15) 
        response.raise_for_status() # sprawdza czy odpowiedz jest poprawna
        data = response.json() # parsuje odpowiedz do formatu json
        return data.get("data", []) # zwraca listę ofert
    except requests.exceptions.RequestException as object: # obsługa bledow podczas pobierania danych
        print(f"Error fetching offers: {object}") # object to obiekt wyjatku, ktory zawiera informacje o bledzie
        return []

def parse_offer(offer) -> dict: # offer to pojedyncza oferta z listy ofert pobranych z API
    # a my pobieramy z tej oferty tylko te dane ktorych potrzrbujemy
    return {
        "external_id": f"olx_{offer.get('id')}",
        "service": "olx",
        "title": offer.get("title"),
        "description": decode_html(offer.get("description", " ")), 
        "price": get_price(offer.get("params", [])),
        "city": offer.get("location", {}).get("city", {}).get("name", " "),
        "region": offer.get("location", {}).get("region", {}).get("name", " "),
        "url": offer.get("url"),
        "is_private": not offer.get("business", False),
    }
def scrape_olx():
    offers = fetch_offers()
    parsed_offers = []
    print("POBIERANIE OFERT Z OLX....")
    for offer in offers:
        parsed_offer = parse_offer(offer)


        if FILTERS.get("tylko_prywatne") and not parsed_offer["is_private"]:
            continue 

        parsed_offers.append(parsed_offer)

    print(f"ZAKOŃCZONO POBIERANIE OFERT Z OLX. ILOŚĆ OFERT: {len(parsed_offers)}")
    for i in parsed_offers:
        print(i)
    return parsed_offers

scrape_olx()
