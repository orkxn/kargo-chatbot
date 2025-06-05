import requests
import os
from dotenv import load_dotenv

load_dotenv()

AFTERSHIP_API_KEY = os.getenv("AFTERSHIP_API_KEY")
headers = {
    "aftership-api-key": AFTERSHIP_API_KEY,
    "Content-Type": "application/json"
}


def detect_courier(tracking_number):
    url = "https://api.aftership.com/v4/couriers/detect"
    payload = {"tracking": {"tracking_number": tracking_number}}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        couriers = response.json().get("data", {}).get("couriers", [])
        if couriers:
            return couriers[0]["slug"]
    return None


def create_tracking(tracking_number, slug):
    url = f"https://api.aftership.com/v4/trackings"
    headers = {
        "aftership-api-key": AFTERSHIP_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "tracking": {
            "slug": slug,
            "tracking_number": tracking_number
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        return True  # Başarıyla eklendi
    elif response.status_code == 400 and "Tracking already exists" in response.text:
        return True  # Zaten ekli, sorun değil
    else:
        print("Create tracking response:", response.status_code, response.text)
        return False  # Hata


def get_tracking_info(tracking_number, slug):
    url = f"https://api.aftership.com/v4/trackings/{slug}/{tracking_number}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tracking = response.json().get("data", {}).get("tracking", {})
        tag = tracking.get("tag", "unknown")
        status = tracking.get("subtag_message", "Durum yok")
        courier = tracking.get("slug", "Bilinmiyor")
        last_update = tracking.get("expected_delivery", "Tahmini teslim tarihi yok")

        return f"""📦 Durum: {tag}
📮 Firma: {courier}
🗓️ Tahmini Teslim: {last_update}
🔎 Detay: {status}"""
    else:
        return f"❌ Bilgi alınamadı: {response.status_code}"


def track_package(tracking_number):
    slug = detect_courier(tracking_number)
    if not slug:
        return "Kargo firması algılanamadı."

    print(f"Algılanan firma slug: {slug}")

    added = create_tracking(tracking_number, slug)
    if added:
        return get_tracking_info(tracking_number, slug)
    else:
        return "Takip numarası eklenemedi."


# Örnek kullanım:
if __name__ == "__main__":
    takip_no = "RE699658596TR"
    durum = track_package(takip_no)
    print(durum)
