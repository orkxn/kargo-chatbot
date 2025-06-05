import requests
import os
from dotenv import load_dotenv

load_dotenv()
AFTERSHIP_API_KEY = os.getenv("AFTERSHIP_API_KEY")

def get_tracking_info(tracking_number):
    headers = {
        "aftership-api-key": AFTERSHIP_API_KEY,
        "Content-Type": "application/json"
    }
    url = f"https://api.aftership.com/v4/trackings/dhl/{tracking_number}"  # dhl yerine kendi kargo firmana göre ayarla
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return "Kargo bilgisi alınamadı."
    
    data = response.json()
    checkpoint = data["data"]["tracking"]["checkpoints"][-1]
    return f"Kargonuz {checkpoint['location']} konumunda. Durum: {checkpoint['message']}"
