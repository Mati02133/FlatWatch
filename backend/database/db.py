from .models import get_connection

def as_text(value):
    if value is None:
        return None
    return str(value)

def as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def offer_exists(external_id):
    conn = get_connection()
    row = conn.execute("SELECT id FROM offers WHERE external_id = %s", (external_id,)).fetchone()

    return row is not None

def add_offer(offer):
    conn = get_connection()

    try:
        row = conn.execute(
            """INSERT INTO offers (external_id, service, title, description, price, area, rooms, city, url, is_private)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (external_id) DO NOTHING
               RETURNING id""",
            (
                offer["external_id"],
                offer["service"],
                as_text(offer.get("title")),
                as_text(offer.get("description")),
                as_number(offer.get("price")),
                as_text(offer.get("area")),
                as_text(offer.get("rooms")),
                as_text(offer.get("city")),
                as_text(offer.get("url")),
                bool(offer.get("is_private")),
            ),
        ).fetchone()
        return row is not None
    except Exception as e:
        print(f"ERROR ADDING OFFER: {e}")
        return False

def update_offer_last_seen(external_id):
    conn = get_connection()

    try:
        conn.execute("UPDATE offers SET last_seen = now() WHERE external_id = %s", (external_id,))
    except Exception as e:
        print(f"ERROR UPDATING LAST SEEN: {e}")

def deactivate_missing_offers(service, current_ids):
    """Oznacza jako nieaktywne oferty, których nie ma w bieżącym pobraniu."""
    if not current_ids:
        return

    conn = get_connection()

    try:
        conn.execute(
            """UPDATE offers SET is_active = FALSE
               WHERE service = %s AND is_active = TRUE AND NOT (external_id = ANY(%s))""",
            (service, list(current_ids)),
        )
    except Exception as e:
        print(f"ERROR DEACTIVATING OFFERS: {e}")
