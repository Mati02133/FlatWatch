from backend.scrapers.olx import scrape_olx
from backend.database.models import create_tables
from backend.database import db
from backend.telegram import send_telegram_message

def run_scraper():
    create_tables()

    offers = scrape_olx()
    if not offers:
        print("Brak ofert do przetworzenia.")
        return

    current_ids = [offer["external_id"] for offer in offers]
    new_offers = []

    for offer in offers:
        if db.offer_exists(offer["external_id"]):
            db.update_offer_last_seen(offer["external_id"])
        else:
            if db.add_offer(offer):
                new_offers.append(offer)

    db.deactivate_missing_offers("olx", current_ids)

    # Wysyłanie powiadomień o nowych ofertach
    for offer in new_offers:
        message = (
            f"🏠 <b>Nowa oferta!</b>\n"
            f"Tytuł: {offer['title']}\n"
            f"Cena: {offer['price']} zł\n"
            f"Metraż: {offer['area']} m²\n"
            f"Lokalizacja: {offer['city']}, {offer['region']}\n"
            f"<a href='{offer['url']}'>Zobacz ogłoszenie</a>"
        )
        send_telegram_message(message)

    print("Aktualizacja bazy zakończona.")

if __name__ == "__main__":
    run_scraper()