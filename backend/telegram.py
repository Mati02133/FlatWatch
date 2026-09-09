import html
import requests
from backend.scrapers.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def escape_html(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)

def hide_token(text: str) -> str: # token jest czescia adresu, wiec requests wkleja go do tresci wyjatkow
    if TELEGRAM_TOKEN:
        return text.replace(TELEGRAM_TOKEN, "<TOKEN>")
    return text

def send_telegram_message(text: str, parse_mode: str = "HTML") -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Brak tokenu Telegram – powiadomienie pominięte.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Błąd wysyłania Telegrama: {response.status_code} {hide_token(response.text)}")
    except Exception as e:
        print(f"Wywołanie Telegrama nie powiodło się: {hide_token(str(e))}")