import requests

def send_whatsapp(phone, name):

    message = f"Hola {name}, gracias por tu interés. Un asesor te contactará en breve."

    url = "https://api.callmebot.com/whatsapp.php"

    params = {
        "phone": phone,
        "text": message,
        "apikey": "TU_API_KEY"
    }

    requests.get(url, params=params)