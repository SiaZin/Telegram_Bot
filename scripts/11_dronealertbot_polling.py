import asyncio
import logging
import time
import re
from telethon import TelegramClient, events
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio
nest_asyncio.apply()

# ---------------------- CONFIGURATION ----------------------
api_id = 'api id'
api_hash = 'api hash'
bot_token = 'bot token'

# Channels to monitor (use the channel usernames, no '@' or URL parts)
channels_to_monitor = ['chyste_nebo', 'vseok450','AerisRimor','buchanskahromada','kyivmonitoring1','homohominideusest']

# Regex patterns for detecting mentions of cities
regex_patterns = {
    "Ірп": re.compile(r'\bІрп\w*\b', re.IGNORECASE),
    "Буч": re.compile(r'\bБуч\w*\b', re.IGNORECASE),
    "Гостом": re.compile(r'\bГостом\w*\b', re.IGNORECASE),
    "Коцюбин": re.compile(r'\bКоцюбин\w*\b', re.IGNORECASE),
    "Ворзел": re.compile(r'\bВорзел\w*\b', re.IGNORECASE),
}

user_chat_id = None

# ---------------------- BOT SETUP ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_chat_id
    user_chat_id = update.effective_chat.id
    await update.message.reply_text("✅ Notifications will be sent here when a keyword is detected.")

# Function to send a notification using the bot.
async def send_notification(text: str, application):
    global user_chat_id
    if user_chat_id:
        await application.bot.send_message(chat_id=user_chat_id, text=text)
    else:
        print("User chat id not set. Please send /start to the bot to register your chat.")

# ---------------------- MAIN FUNCTION ----------------------
async def main():
    global telethon_client

    #Initialize the Telegram bot application
    application = ApplicationBuilder().token(bot_token).build()

    #Register handlers
    application.add_handler(CommandHandler("start", start))

    #Ensure no webhook is active (prevents conflicts)
    async with application.bot as bot:
        await bot.delete_webhook(drop_pending_updates=True)

    #Start the bot manually (instead of using run_polling)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(poll_interval=30.0,timeout=120)  # Manually start long polling

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

    #Run Telethon in the background
    await telethon_client.run_until_disconnected()

    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    print("🛑 Bot and Telethon stopped.")

# ---------------------- ENTRY POINT ----------------------
if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    asyncio.run(main())
