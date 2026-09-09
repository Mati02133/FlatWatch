from backend.scrapers.olx import scrape_olx
from backend.database.models import create_tables
from backend.database import db
from backend.telegram import send_telegram_message, escape_html

def format_offer_message(offer) -> str:
    title = escape_html(offer.get("title"))
    price = escape_html(offer.get("price"))
    area = escape_html(offer.get("area"))
    city = escape_html(offer.get("city"))
    region = escape_html(offer.get("region"))
    url = escape_html(offer.get("url"))

    return (
        f"🏠 <b>Nowa oferta!</b>\n"
        f"Tytuł: {title}\n"
        f"Cena: {price} zł\n"
        f"Metraż: {area} m²\n"
        f"Lokalizacja: {city}, {region}\n"
        f'<a href="{url}">Zobacz ogłoszenie</a>'
    )

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
        send_telegram_message(format_offer_message(offer))

    print("Aktualizacja bazy zakończona.")

if __name__ == "__main__":
    run_scraper()