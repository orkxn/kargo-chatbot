import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

AFTERSHIP_API_KEY = os.getenv("AFTERSHIP_API_KEY")
headers = {
    "aftership-api-key": AFTERSHIP_API_KEY,
    "Content-Type": "application/json"
}

api_logger = logging.getLogger("api_logger")
api_logger.setLevel(logging.INFO)
api_handler = logging.FileHandler("api.log", encoding="utf-8")
api_logger.addHandler(api_handler)

# Basit durum çeviri tablosu
STATUS_TRANSLATIONS = {
    "InTransit": {"tr": "Yolda", "en": "In Transit", "sv": "På väg"},
    "Delivered": {"tr": "Teslim Edildi", "en": "Delivered", "sv": "Levererad"},
    "InfoReceived": {"tr": "Bilgi Alındı", "en": "Info Received", "sv": "Information mottagen"},
    "OutForDelivery": {"tr": "Teslimata Çıkmış", "en": "Out for Delivery", "sv": "Utleverans"},
    # İhtiyaca göre ekle...
}

# Courier kodlarını isimlere çevirme (örnek)
COURIER_NAMES = {
    "ptt-posta": {"tr": "PTT Posta", "en": "PTT Post", "sv": "PTT Post"},
    # Diğer firmalar eklenebilir
}

def detect_courier(tracking_number):
    url = "https://api.aftership.com/v4/couriers/detect"
    payload = {"tracking": {"tracking_number": tracking_number}}
    response = requests.post(url, headers=headers, json=payload)
    api_logger.info(f"[detect_courier] {tracking_number} → {response.status_code} | {response.text[:300]}")
    if response.status_code == 200:
        couriers = response.json().get("data", {}).get("couriers", [])
        if couriers:
            return couriers[0]["slug"]
    return None

def create_tracking(tracking_number, slug):
    url = "https://api.aftership.com/v4/trackings"
    data = {"tracking": {"slug": slug, "tracking_number": tracking_number}}
    response = requests.post(url, headers=headers, json=data)
    api_logger.info(f"[create_tracking] {tracking_number} → {response.status_code} | {response.text[:300]}")
    if response.status_code == 201 or (response.status_code == 400 and "Tracking already exists" in response.text):
        return True
    return False

def get_tracking_info(tracking_number, slug):
    url = f"https://api.aftership.com/v4/trackings/{slug}/{tracking_number}"
    response = requests.get(url, headers=headers)
    api_logger.info(f"[get_tracking_info] {tracking_number} → {response.status_code} | {response.text[:300]}")
    if response.status_code == 200:
        tracking = response.json().get("data", {}).get("tracking", {})
        return (
            tracking.get("tag", "unknown"),
            tracking.get("slug", "unknown"),
            tracking.get("expected_delivery", None),
        )
    return None, None, None

def format_date(date_str, lang):
    if not date_str:
        return "-"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if lang == "tr":
            months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            return f"{dt.day} {months[dt.month-1]} {dt.year}"
        elif lang == "sv":
            months = ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"]
            return f"{dt.day} {months[dt.month-1]} {dt.year}"
        else:  # en
            return dt.strftime("%d %B %Y")
    except Exception:
        return date_str

def track_package(tracking_number, lang="tr"):
    slug = detect_courier(tracking_number)
    if not slug:
        return {
            "tr": "Kargo firması algılanamadı.",
            "en": "Courier could not be detected.",
            "sv": "Speditören kunde inte upptäckas."
        }.get(lang, "Kargo firması algılanamadı.")

    if not create_tracking(tracking_number, slug):
        return {
            "tr": "Takip numarası eklenemedi.",
            "en": "Tracking number could not be added.",
            "sv": "Spårningsnumret kunde inte läggas till."
        }.get(lang, "Takip numarası eklenemedi.")

    status_tag, courier_slug, est_delivery = get_tracking_info(tracking_number, slug)
    if not status_tag:
        return {
            "tr": "Bilgi alınamadı.",
            "en": "Could not get tracking info.",
            "sv": "Kunde inte hämta spårningsinformation."
        }.get(lang, "Bilgi alınamadı.")

    # Durum çevirisi
    status = STATUS_TRANSLATIONS.get(status_tag, {}).get(lang, status_tag)
    # Firma ismi çevirisi
    courier_name = COURIER_NAMES.get(courier_slug, {}).get(lang, courier_slug)
    # Tarih formatı
    est_delivery_fmt = format_date(est_delivery, lang)

    if lang == "en":
        return f"📦 Status: {status}\n📮 Courier: {courier_name}\n🗓️ Estimated Delivery: {est_delivery_fmt}\n🔎 Detail: {status}"
    elif lang == "sv":
        return f"📦 Status: {status}\n📮 Speditör: {courier_name}\n🗓️ Beräknad leverans: {est_delivery_fmt}\n🔎 Detalj: {status}"
    else:  # Türkçe
        return f"📦 Durum: {status}\n📮 Firma: {courier_name}\n🗓️ Tahmini Teslim: {est_delivery_fmt}\n🔎 Detay: {status}"
