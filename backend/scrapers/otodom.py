import requests
from bs4 import BeautifulSoup
import json
from config import FILTERS, CITY_NORMALIZED, OTODOM_CITIES

BASE_URL = "https://www.otodom.pl/pl/wyniki"

HEADERS = { # headers uzywamy po to aby nie zostac zablokowanym przez serwer imitujac przegladarke
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) " # konkertna przegladarka i jej wersja
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
}

def build_url() -> str: # buduje url do pobrania ogloszen z otodom.pl na config.py
    city = FILTERS["miasto"].lower()
    typ = FILTERS["typ"]
    city_path = OTODOM_CITIES.get(city)
    url = f"{BASE_URL}/{typ}/mieszkanie/{city_path}"

    params = []
    if FILTERS.get("cena_min"):
        params.append(f"price_min={FILTERS['cena_min']}")
    if FILTERS.get("cena_max"):
        params.append(f"price_max={FILTERS['cena_max']}")
    if FILTERS.get("powierzchnia_min"):
        params.append(f"area_min={FILTERS['powierzchnia_min']}")
    if FILTERS.get("powierzchnia_max"):
        params.append(f"area_max={FILTERS['powierzchnia_max']}")
    if FILTERS.get("tylko_prywatne"):
        params.append("ownerTypeSingleSelect=PRIVATE")
    
    if params:
        url += "?" + "&".join(params)
    return url

def decode_html(html) -> str: # dekoduje html do czystego tekstu
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def get_detail(details,key) -> str: # pobiera tylko te parametry ktore sa nam potrzebne
    for item in details:
        if item.get("key") == key:
            return item.get("value")
    return None

def fetch_listing_page() -> list:
    url = build_url()
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as object:
        print(f"Error fetching offers from Otodom: {object}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        print("Error: Could not find the __NEXT_DATA__ script tag.")
        return []
    try:
        data = json.loads(script.string) # parsuje json z html
        item = data["props"]["pageProps"]["data"]["searchAds"]["items"] # pobiera tylko te parametry
        return item
    except (json.JSONDecodeError, KeyError) as object: 
        print(f"Error parsing JSON data: {object}")
        return []
    
def fetch_offer_details(offer_url) -> dict:
    try:
        response = requests.get(offer_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as object:
        print(f"Error fetching offer details from Otodom: {object}")
        return {}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return {}
    try:
        data = json.loads(script.string)
        return data["props"]["pageProps"]["ad"]
    except (json.JSONDecodeError, KeyError) as object:
        print(f"Error parsing JSON data: {object}")
        return {}
    
def parse_offer(ad) -> dict:
    details = ad.get("details", [])
    city = ""
    locations = ad.get("locations", []).get("ReverseGeocoding", []).get("locations", [])
    for i in locations:
        if i.get("locationType") == "city":
            city = i.get("name", "")
            break
    return {
        "external_id": f"otodom_{ad.get('id')}",
        "server": "otodom",
        "title": ad.get("title",""),
        "description": decode_html(ad.get("description", "")),
        "price":get_detail(details, "price"),
        "area": get_detail(details, "m"),
        "rooms": get_detail(details, "rooms_num"),
        "city": city,
        "url": ad.get("url",""),
        "is_private": ad.get("advertiserType") == "private",
    }
def scrape_otodom() -> list:
    url = build_url()
    print(f"Scraping Otodom offers from URL: {url}")
    offers = fetch_listing_page()
    print(f"Found {len(offers)} offers on Otodom")

    parsed_offers = []
    expected_city = CITY_NORMALIZED.get(FILTERS["miasto"].lower(), FILTERS["miasto"].lower())
    for i in offers:
        slug = i.get("slug")
        if not slug:
            continue
        offer_url = f"https://www.otodom.pl/pl/oferta/{slug}"
        ad = fetch_offer_details(offer_url)
        if not ad:
            continue
        parsed_offer = parse_offer(ad)
        if parsed_offer["city"].lower() != expected_city:
            continue
        if FILTERS.get("tylko_prywatne") and not parsed_offer["is_private"]:
            continue
        parsed_offers.append(parsed_offer)
    print(f"Finished scraping Otodom. Total offers after filtering: {len(parsed_offers)}")
    for offer in parsed_offers:
        print(offer)
    return parsed_offers

