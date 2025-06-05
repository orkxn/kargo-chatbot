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
        status_tag = tracking.get("tag", "unknown")
        courier = tracking.get("slug", "unknown")
        est_delivery = tracking.get("expected_delivery", None)

        # Dil desteği için farklı mesajlar
        return status_tag, courier, est_delivery
    else:
        return None, None, None

def track_package(tracking_number, lang="tr"):
    slug = detect_courier(tracking_number)
    if not slug:
        if lang == "en":
            return "Courier could not be detected."
        elif lang == "sv":
            return "Speditören kunde inte upptäckas."
        else:
            return "Kargo firması algılanamadı."

    added = create_tracking(tracking_number, slug)
    if not added:
        if lang == "en":
            return "Tracking number could not be added."
        elif lang == "sv":
            return "Spårningsnumret kunde inte läggas till."
        else:
            return "Takip numarası eklenemedi."

    status_tag, courier, est_delivery = get_tracking_info(tracking_number, slug)
    if status_tag is None:
        if lang == "en":
            return "Could not get tracking info."
        elif lang == "sv":
            return "Kunde inte hämta spårningsinformation."
        else:
            return "Bilgi alınamadı."

    # Durumu farklı dillerde formatla
    if lang == "en":
        return f"📦 Status: {status_tag}\n📮 Courier: {courier}\n🗓️ Estimated Delivery: {est_delivery}\n🔎 Detail: {status_tag}"
    elif lang == "sv":
        return f"📦 Status: {status_tag}\n📮 Speditör: {courier}\n🗓️ Beräknad leverans: {est_delivery}\n🔎 Detalj: {status_tag}"
    else:
        return f"📦 Durum: {status_tag}\n📮 Firma: {courier}\n🗓️ Tahmini Teslim: {est_delivery}\n🔎 Detay: {status_tag}"

# Örnek kullanım
if __name__ == "__main__":
    takip_no = "RE699658596TR"
    print(track_package(takip_no, lang="sv"))
