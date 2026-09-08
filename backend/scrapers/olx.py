import requests
from bs4 import BeautifulSoup
from config import OLX_CATEGORY_ID, OLX_REGIONS, FILTERS, OLX_CITIES, CITY_NORMALIZED

BASE_URL = "https://www.olx.pl/api/v1/offers/" # api endpoint used to fetch olx listings

def build_params() -> dict:
    city = FILTERS["miasto"].lower()
    region_id = OLX_REGIONS.get(city, 4) # default region is krakow when the city is missing
    city_id = OLX_CITIES.get(city)

    params =  {
        "category_id": OLX_CATEGORY_ID,
        "region_id": region_id,
        "limit": 50, # number of listings requested in one batch
        "offset": 0, # starting index for pagination
        "sort_by": "created_at:desc", # newest listings first
    }
    
    # additional filters can be added when needed
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

def decode_html(html) -> str: # strips html and keeps only readable text
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def get_param(params_list, key) -> list: # reads only the fields needed for filtering and storage
    for param in params_list:
        if param.get("key") == key:
            val = param["value"].get("value") # some values are nested under value, others under key
            if val is None:
                val = param["value"].get("key")
            return val
    return None

def fetch_offers() -> list:
    params = build_params()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.olx.pl/",
        "Origin": "https://www.olx.pl",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper()

        scraper.get("https://www.olx.pl/", headers=headers, timeout=15)
        response = scraper.get(BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except ImportError:
        print("Brak biblioteki cloudscraper. Zainstaluj ją: pip install cloudscraper")
        try:
            session = requests.Session()
            session.get("https://www.olx.pl/", headers=headers, timeout=15)
            response = session.get(BASE_URL, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching offers: {e}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching offers (cloudscraper): {e}")
        return []
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def parse_offer(offer) -> dict: # keeps only the fields required by the app from each raw offer
    params = offer.get("params", [])
    return {
        "external_id": f"olx_{offer.get('id')}",
        "service": "olx",
        "title": offer.get("title"),
        "description": decode_html(offer.get("description", " ")), 
        "price": get_param(params, "price"),
        "area": get_param(params, "m"),
        "rooms": get_param(params, "rooms"),
        "city": offer.get("location", {}).get("city", {}).get("name", " "),
        "region": offer.get("location", {}).get("region", {}).get("name", " "),
        "url": offer.get("url"),
        "is_private": not offer.get("business", False),
    }

def scrape_olx() -> list:
    offers = fetch_offers() # loads the raw listing data from the source
    parsed_offers = []
    expected_city = CITY_NORMALIZED.get(FILTERS["miasto"].lower(), FILTERS["miasto"].lower())

    print("fetching olx offers...")
    for offer in offers:
        parsed_offer = parse_offer(offer)

        if FILTERS.get("tylko_prywatne") and not parsed_offer["is_private"]:
            continue 
        if parsed_offer["city"].lower() != expected_city:
            continue

        parsed_offers.append(parsed_offer)

    print(f"completed olx scraping. offers found: {len(parsed_offers)}")
    for i in parsed_offers:
        print(i)
    return parsed_offers

scrape_olx() # runs the olx scraper once when the module is executed directly