import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from tracker import track_package

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Admin kullanıcı ID'leri (Telegram kullanıcı ID'nizi buraya ekleyin)
ADMIN_IDS = {7163935699}  # Örnek ID, kendi ID'nizi buraya koyun

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
        "tr": "🌐 *Dil ayarlandı:* Türkçe (TR)\n\n✉️ Takip numaranızı gönderin, durumu kontrol edeyim.",
        "en": "🌐 *Language set:* English (EN)\n\n✉️ Send your tracking number, I'll check the status.",
        "sv": "🌐 *Språk inställt:* Svenska (SV)\n\n✉️ Skicka ditt spårningsnummer, jag kollar statusen."
    },
    "ask_tracking": {
        "tr": "Lütfen takip numaranızı gönderin.",
        "en": "Please send your tracking number.",
        "sv": "Vänligen skicka ditt spårningsnummer."
    },
    "admin_no_access": "❌ Bu komutu kullanmaya yetkiniz yok.",
    "admin_panel": "Admin Paneli:",
    "admin_status": "Bot şu anda çalışıyor ✅",
    "admin_exit": "Admin panelinden çıkıldı."
}

def get_message(lang, key):
    return MESSAGES.get(key, {}).get(lang, MESSAGES[key]["en"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"/start komutu alındı - Kullanıcı: {user.id} - {user.username}")
    
    keyboard = [
        [
            InlineKeyboardButton(LANGUAGES["tr"], callback_data="tr"),
            InlineKeyboardButton(LANGUAGES["en"], callback_data="en"),
            InlineKeyboardButton(LANGUAGES["sv"], callback_data="sv")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(MESSAGES["welcome"]["en"], reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data
    context.user_data['lang'] = lang_code
    logger.info(f"Kullanıcı {query.from_user.id} dil seçti: {lang_code}")

    await query.edit_message_text(
        text=MESSAGES["language_set"][lang_code],
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get('lang', 'en')
    tracking_number = update.message.text.strip()
    logger.info(f"Kullanıcı {user.id} takip numarası gönderdi: {tracking_number} - Dil: {lang}")

    result = track_package(tracking_number, lang)
    logger.info(f"Tracking sonucu: {result}")

    await update.message.reply_text(result)

# --- Admin Panel Fonksiyonları ---

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["admin_no_access"])
        return

    keyboard = [
        [InlineKeyboardButton("🟢 Bot Durumu", callback_data="admin_status")],
        [InlineKeyboardButton("📄 Log Dosyasını Gönder", callback_data="admin_send_log")],
        [InlineKeyboardButton("🚪 Çıkış", callback_data="admin_exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(MESSAGES["admin_panel"], reply_markup=reply_markup)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("Yetkiniz yok!", show_alert=True)
        return

    data = query.data

    if data == "admin_status":
        await query.edit_message_text(MESSAGES["admin_status"])
    elif data == "admin_send_log":
        try:
            await query.message.reply_document(document=open('bot.log', 'rb'))
            await query.answer("Log dosyası gönderildi.", show_alert=False)
        except Exception as e:
            await query.answer(f"Log dosyası gönderilemedi: {e}", show_alert=True)
    elif data == "admin_exit":
        await query.edit_message_text(MESSAGES["admin_exit"])

def start_bot():
    logger.info("Bot başlatılıyor...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^(tr|en|sv)$"))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Admin komutları
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))

    application.run_polling()

if __name__ == "__main__":
    start_bot()
