import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from tracker import track_package
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = {int(os.getenv("ADMIN_ID", 0))}  # .env içinde: ADMIN_ID=123456789

# Bot log ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log",
    filemode="a",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

# Dil seçenekleri
LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
    "sv": "🇸🇪 Svenska"
}

MESSAGES = {
    "welcome": {
        "tr": "Merhaba! Lütfen bir dil seçin:",
        "en": "Hello! Please select a language:",
        "sv": "Hej! Vänligen välj ett språk:"
    },
    "language_set": {
        "tr": "🌐 *Dil ayarlandı:* Türkçe (TR)\n\n✉️ Takip numaranızı gönderin.",
        "en": "🌐 *Language set:* English (EN)\n\n✉️ Send your tracking number.",
        "sv": "🌐 *Språk inställt:* Svenska (SV)\n\n✉️ Skicka ditt spårningsnummer."
    },
    "admin_panel": "🔧 Admin Paneli:",
    "admin_status": "✅ Bot şu anda aktif.",
    "admin_exit": "📴 Admin panelden çıkış yapıldı.",
    "admin_no_access": "❌ Bu komutu kullanmaya yetkiniz yok."
}

# Kullanıcıya ait dil bilgisi tutulur
user_languages = {}

def get_message(lang, key):
    return MESSAGES.get(key, {}).get(lang, MESSAGES[key].get("en", ""))

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"/start komutu: {user.id} - {user.username}")

    keyboard = [[
        InlineKeyboardButton(LANGUAGES["tr"], callback_data="tr"),
        InlineKeyboardButton(LANGUAGES["en"], callback_data="en"),
        InlineKeyboardButton(LANGUAGES["sv"], callback_data="sv")
    ]]
    await update.message.reply_text(
        text=MESSAGES["welcome"]["en"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Dil seçimi
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data
    context.user_data["lang"] = lang_code
    logger.info(f"Dil seçildi: {query.from_user.id} → {lang_code}")

    await query.edit_message_text(
        text=MESSAGES["language_set"][lang_code],
        parse_mode="Markdown"
    )

# Takip numarası işleme
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get("lang", "en")
    tracking_number = update.message.text.strip()
    logger.info(f"{user.id} → {tracking_number} (lang: {lang})")

    result = track_package(tracking_number, lang=lang)
    logger.info(f"Tracking sonucu: {result}")
    await update.message.reply_text(result)

# /admin komutu
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["admin_no_access"])
        return

    keyboard = [
        [InlineKeyboardButton("🟢 Bot Durumu", callback_data="admin_status")],
        [InlineKeyboardButton("📄 bot.log Gönder", callback_data="admin_send_bot_log")],
        [InlineKeyboardButton("📄 api.log Gönder", callback_data="admin_send_api_log")],
        [InlineKeyboardButton("🚪 Çıkış", callback_data="admin_exit")]
    ]
    await update.message.reply_text(MESSAGES["admin_panel"], reply_markup=InlineKeyboardMarkup(keyboard))

# Admin panel callback
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.answer("Yetkiniz yok!", show_alert=True)
        return

    data = query.data
    if data == "admin_status":
        await query.edit_message_text(MESSAGES["admin_status"])

    elif data == "admin_send_bot_log":
        try:
            await query.message.reply_document(document=open("bot.log", "rb"))
            await query.answer("bot.log gönderildi.")
        except Exception as e:
            await query.answer(f"Hata: {e}", show_alert=True)

    elif data == "admin_send_api_log":
        try:
            await query.message.reply_document(document=open("api.log", "rb"))
            await query.answer("api.log gönderildi.")
        except Exception as e:
            await query.answer(f"Hata: {e}", show_alert=True)

    elif data == "admin_exit":
        await query.edit_message_text(MESSAGES["admin_exit"])

# Bot başlatma
def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^(tr|en|sv)$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("Bot başlatılıyor...")
    app.run_polling()

# Eğer bu dosya doğrudan çalıştırılırsa
if __name__ == "__main__":
    start_bot()
