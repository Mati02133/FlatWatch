from backend.scrapers.config import SERVICES
from backend.scrapers.olx import scrape_olx
from backend.database.models import create_tables
from backend.database import db 

def run_scraper():
    create_tables()

    offers = scrape_olx()  
    if not offers:
        print("Brak ofert do przetworzenia.")
        return

    current_ids = []
    for offer in offers:
        current_ids.append(offer["external_id"])
        if db.offer_exists(offer["external_id"]):
            db.update_offer_last_seen(offer["external_id"])
        else:
            db.add_offer(offer)

    db.deactivate_missing_offers("olx", current_ids)

    print("Aktualizacja bazy zakończona.")

if __name__ == "__main__":
    run_scraper()