import asyncio
import logging
import time
import re
from fastapi import FastAPI, Request
from telethon import TelegramClient, events
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import uvicorn
import nest_asyncio

nest_asyncio.apply()

# ---------------------- CONFIGURATION ----------------------
api_id = 'api id'
api_hash = 'api hash'
bot_token = 'bot token'
WEBHOOK_URL = "https://ffc2-95-158-42-65.ngrok-free.app/webhook"  # Your ngrok HTTPS URL

# Channels to monitor 
channels_to_monitor = ['chyste_nebo', 'vseok450','AerisRimor','kyivmonitoring1']

# Regex patterns for detecting mentions of cities
regex_patterns = {
    "Ірп": re.compile(r'\bІрп\w*\b', re.IGNORECASE),
    "Буч": re.compile(r'\bБуч\w*\b', re.IGNORECASE),
    "Гостом": re.compile(r'\bГостом\w*\b', re.IGNORECASE),
    "Коцюбин": re.compile(r'\bКоцюбин\w*\b', re.IGNORECASE),
    "Ворзел": re.compile(r'\bВорзел\w*\b', re.IGNORECASE),
}

user_chat_id = None

# ---------------------- FASTAPI SETUP ----------------------
app = FastAPI()

# ---------------------- BOT SETUP ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_chat_id
    user_chat_id = update.effective_chat.id
    await update.message.reply_text("✅ Notifications will be sent here when a keyword is detected.")

async def send_notification(text: str, application):
    global user_chat_id
    if user_chat_id:
        await application.bot.send_message(chat_id=user_chat_id, text=text)
    else:
        print("User chat id not set. Please send /start to the bot to register your chat.")

# ---------------------- WEBHOOK HANDLER ----------------------

@app.post("/webhook")
async def telegram_webhook(update_data: dict):
    """Handle incoming updates from Telegram."""
    update = Update.de_json(update_data, application.bot)

    await application.initialize()  # Ensure the bot is initialized before processing
    await application.process_update(update)

    return {"ok": True}

# ---------------------- MAIN FUNCTION ----------------------
async def main():
    global telethon_client, application, bot

    #Initialize the Telegram bot application
    application = ApplicationBuilder().token(bot_token).build()

    #Register handlers
    application.add_handler(CommandHandler("start", start))

    #Ensure no old webhook is active
    async with application.bot as bot:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ Webhook set to {WEBHOOK_URL}")

    #Initialize and start the Telethon client
    telethon_client = TelegramClient('session_name', api_id, api_hash)
    await telethon_client.start()
    print("✅ Telethon client started!")

    #Define the Telethon event handler
    @telethon_client.on(events.NewMessage(chats=channels_to_monitor))
    async def telethon_handler(event):
        message_text = event.raw_text
        for key, pattern in regex_patterns.items():
            if pattern.search(message_text):
                channel_title = event.chat.title if event.chat and hasattr(event.chat, 'title') else "Unknown Channel"
                notification_text = f"⚠️ Keyword '{key}' found in '{channel_title}':\n\n{message_text}"
                await send_notification(notification_text, application)
                break  # Stop after the first match

    print("🚀 Bot and Telethon are running...")

    #Run FastAPI server for webhook
    config = uvicorn.Config(app, host="0.0.0.0", port=8443, log_level="info")   
    server = uvicorn.Server(config)
    await server.serve()

    await telethon_client.run_until_disconnected()

# ---------------------- ENTRY POINT ----------------------
if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    asyncio.run(main())
