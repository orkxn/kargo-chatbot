import requests
import os
from dotenv import load_dotenv

load_dotenv()

AFTERSHIP_API_KEY = os.getenv("AFTERSHIP_API_KEY")

print("API Key:", AFTERSHIP_API_KEY)

headers = {
    "aftership-api-key": AFTERSHIP_API_KEY,
    "Content-Type": "application/json"
}

# 1. Kargo firması otomatik olarak tespit edilir
def detect_courier(tracking_number):
    url = "https://api.aftership.com/v4/couriers/detect"
    payload = {
        "tracking": {
            "tracking_number": tracking_number
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("detect_courier hata:", response.status_code, response.text)
        return None

    data = response.json()
    couriers = data["data"]["couriers"]

    if not couriers:
        return None

    # En olası firmayı al
    return couriers[0]["slug"]

# 2. Takip numarasını AfterShip'e ekle
def create_tracking(tracking_number, slug):
    url = "https://api.aftership.com/v4/trackings"
    payload = {
        "tracking": {
            "tracking_number": tracking_number,
            "slug": slug
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201, 409]:  # 409: Zaten eklenmiş
        return True
    else:
        print("create_tracking hata:", response.status_code, response.text)
        return False

# 3. Kargo bilgisi getir
def get_tracking_info(tracking_number):
    slug = detect_courier(tracking_number)

    if not slug:
        return "❌ Kargo firması algılanamadı. Takip numarasını kontrol et."

    created = create_tracking(tracking_number, slug)
    if not created:
        return "❌ Takip numarası eklenemedi."

    url = f"https://api.aftership.com/v4/trackings/{slug}/{tracking_number}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("get_tracking_info hata:", response.status_code, response.text)
        return "📦 Kargo bilgisi alınamadı."

    try:
        data = response.json()
        tracking = data["data"]["tracking"]
        checkpoints = tracking.get("checkpoints", [])
        status = tracking.get("tag", "Bilinmiyor")

        if not checkpoints:
            return f"📦 Durum: {status}\nHenüz hareket bilgisi yok."

        last = checkpoints[-1]
        return (
            f"📦 Durum: {status}\n"
            f"📍 Konum: {last.get('location', 'Bilinmiyor')}\n"
            f"📝 Açıklama: {last.get('message', '-')}\n"
            f"🕒 Zaman: {last.get('checkpoint_time', '-')}"
        )

    except Exception as e:
        return f"⚠️ Hata oluştu: {str(e)}"
