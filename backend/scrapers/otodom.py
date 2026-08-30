import requests
from bs4 import BeautifulSoup
import json
from config import FILTERS, CITY_NORMALIZED, OTODOM_CITIES

BASE_URL = "https://www.otodom.pl/pl/wyniki" # base search page used for otodom listings

HEADERS = { # sends a browser-like request to reduce anti-bot blocking
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) " # browser version used to mimic a normal client
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
}

def build_url() -> str: # creates the otodom search url using the configured filters
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
        url += "?" + "&".join(params) # adds the query string needed for the active filters
    return url

def decode_html(html) -> str: # strips html and keeps readable text only
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def get_detail(details,key) -> str: # looks for the requested value in the listing detail fields
    for item in details:
        if item.get("key") == key:
            return item.get("value")
    return None

def fetch_listing_page() -> list:
    url = build_url() # builds the final search url for the current city and filters
    try:
        response = requests.get(url, headers=HEADERS, timeout=15) 
        response.raise_for_status() 
    except requests.RequestException as object: 
        print(f"error fetching offers from otodom: {object}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        print("error: could not find the __next_data__ script tag.")
        return []
    try:
        data = json.loads(script.string) # parses the embedded json payload from the search page
        item = data["props"]["pageProps"]["data"]["searchAds"]["items"] # keeps only the listing objects needed by the app
        return item
    except (json.JSONDecodeError, KeyError) as object: 
        print(f"error parsing json data: {object}")
        return []
    
def fetch_offer_details(offer_url) -> dict:
    try:
        response = requests.get(offer_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as object:
        print(f"error fetching offer details from otodom: {object}")
        return {}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return {}
    try:
        data = json.loads(script.string)
        return data["props"]["pageProps"]["ad"]
    except (json.JSONDecodeError, KeyError) as object:
        print(f"error parsing json data: {object}")
        return {}
    
def parse_offer(ad) -> dict:
    details = ad.get("characteristics", [])
    city = ""
    locations = ad.get("location", {}).get("reverseGeocoding", {}).get("locations", [])
    for i in locations:
        if i.get("locationLevel") == "city_or_village":
            city = i.get("name", "")
            break
    return {
        "external_id": f"otodom_{ad.get('id')}",
        "service": "otodom",
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
    url = build_url() # builds the final otodom request for the current city
    print(f"scraping otodom offers from url: {url}")
    offers = fetch_listing_page() # loads the list of search results
    print(f"found {len(offers)} offers on otodom")

    parsed_offers = []
    expected_city = CITY_NORMALIZED.get(FILTERS["miasto"].lower(), FILTERS["miasto"].lower())
    for i in offers:
        slug = i.get("slug")
        if not slug:
            continue
        offer_url = f"https://www.otodom.pl/pl/oferta/{slug}"
        ad = fetch_offer_details(offer_url) # fetches the detailed listing data for each result
        if not ad:
            continue
        parsed_offer = parse_offer(ad)
        if parsed_offer["city"].lower() != expected_city:
            continue
        if FILTERS.get("tylko_prywatne") and not parsed_offer["is_private"]:
            continue
        parsed_offers.append(parsed_offer)
    print(f"finished scraping otodom. total offers after filtering: {len(parsed_offers)}")
    for offer in parsed_offers:
        print(offer)
    return parsed_offers

