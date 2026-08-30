from database.models import get_connection
from datetime import datetime

def offer_exists(external_id):
    conn = get_connection() # opens a connection to check whether an offer already exists
    row = conn.execute("SELECT id FROM offers WHERE external_id = ?", (external_id,)).fetchone()
    conn.close()

    if row is not None:
        return True
    return False


def add_offer(offer):

    if offer_exists(offer["external_id"]): # prevents duplicate entries for the same external listing
        return False
    
    conn = get_connection() # creates a write connection before saving the offer

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
        conn.commit() # persists the new offer record
        return True
    except Exception as object:
        print(f"ERROR ADDING OFFER: {object}") # logs storage errors for debugging
        return False
    
def deactivate_offer(external_id): # marks a listing as inactive when it disappears from the source
    conn = get_connection()
    conn.execute("UPDATE offers SET is_active = 0 WHERE external_id = ?",(external_id,))
    conn.commit()
    conn.close()

def get_active_offers(service):
    conn = get_connection() # loads only offers that are still active for a given service
    rows = conn.execute("SELECT external_id FROM offers WHERE service = ? AND is_active = 1",(service,))
    result = []
    for i in rows:
        i = i["external_id"]
        result.append(i)
    return result
