
import requests
from scrapers.olx import build_params, fetch_offers

offers = fetch_offers()
if offers:
    import json
    print(json.dumps(offers[0]["params"], indent=2, ensure_ascii=False))