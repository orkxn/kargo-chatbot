from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tracker import get_tracking_info
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Takip numaranızı yazın, size kargo durumunuzu söyleyeyim 📦")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tracking_number = update.message.text.strip()
    result = get_tracking_info(tracking_number)
    await update.message.reply_text(result)

def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot çalışıyor...")
    app.run_polling()
