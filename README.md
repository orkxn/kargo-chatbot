# 📦 Multi-language Telegram Package Tracker Bot

A Telegram bot that allows users to track package deliveries using tracking numbers. It supports multiple languages (Turkish, English, and Swedish) and automatically detects the courier via AfterShip API.

## 🌐 Supported Languages
- 🇹🇷 Turkish (tr)
- 🇬🇧 English (en)
- 🇸🇪 Swedish (sv)

## 🚀 Features
- Automatically detect courier using tracking number
- Retrieve current delivery status and estimated delivery date
- Multi-language interface
- Admin panel with basic api & bot info and log export

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/orkxn/kargo-chatbot.git
cd kargo-chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a `.env` file in the root directory and add your Telegram Bot Token and AfterShip API Key:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AFTERSHIP_API_KEY=your_aftership_api_key
ADMIN_ID=your_telegram_id
```

### 4. Run the Bot

```bash
python main.py
```

## 🛠 Files Overview

- `bot.py`: Main bot logic and handlers
- `tracker.py`: Functions for AfterShip API integration
- `README.md`: Project documentation

## 🔐 Admin Commands

Only users with IDs in the `ADMIN_IDS` set can use these:
- `/admin`: Access admin panel
- Options to:
  - Check bot status
  - Download logs
  - Exit panel

## 🧪 Sample Usage

```bash
/start
-> Select language
-> Send tracking number
-> Receive delivery status and info
```

## 📄 License

This project is for educational and personal use.
