import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from tracker import track_package

# .env dosyasından TELEGRAM token'ını al
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# /start komutu çalıştığında botun vereceği yanıt
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Takip numaranı gönder, kargonun durumunu söyleyeyim.")

# Kullanıcı mesaj gönderdiğinde (takip numarası) çalışacak fonksiyon
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tracking_number = update.message.text.strip()
    result = track_package(tracking_number)
    await update.message.reply_text(result)

# Botu başlatan ana fonksiyon
def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar ve mesajlar için handler'lar
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot çalışıyor... Telegram'dan bir şeyler gönder :)")
    app.run_polling()
