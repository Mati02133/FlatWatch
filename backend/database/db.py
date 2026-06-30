from database.models import get_connection
from datetime import datetime

def offer_exists(external_id):
    conn = get_connection()
    row = conn.execute("SELECT id FROM offers WHERE external_id = ?", (external_id,)).fetchone()
    conn.close()

    if row is not None:
        return True
    return False


def add_offer(offer):

    if offer_exists(offer["external_id"]):
        return False
    
    conn = get_connection()

    try:
        if offer.get("is_private"):
            is_private_value = 1
        else:
            is_private_value = 0
        conn.execute("""INSERT INTO offers (external_id, service, title, description, price, area, rooms, city, url, is_private, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (
                        offer["external_id"],
                        offer["service"],
                        offer.get("title",""),
                        offer.get("description",""),
                        offer.get("price",""),
                        offer.get("area",""),
                        offer.get("rooms",""),
                        offer.get("city",""),
                        offer.get("url",""),
                        is_private_value,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     )
        )
        conn.commit()
        return True
    except Exception as object:
        print(f"ERROR ADDING OFFER: {object}")
        return False
    
def deactivate_offer(external_id): # jezeli jakas oferta zniknie z serwisu zapisujemy ja jako nieaktywna
    conn = get_connection()
    conn.execute("UPDATE offers SET is_active = 0 WHERE external_id = ?",(external_id,))
    conn.commit()
    conn.close()

def get_active_offers(service):
    conn = get_connection()
    rows = conn.execute("SELECT external_id FROM offers WHERE service = ? AND is_active = 1",(service,))
    result = []
    for i in rows:
        i = i["external_id"]
        result.append(i)
    return result
