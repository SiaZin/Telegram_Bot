import os
import json
import asyncio
import logging
import time
import re
from telethon import TelegramClient, events
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,CallbackQueryHandler
import nest_asyncio
nest_asyncio.apply()

# ---------------------- CONFIGURATION ----------------------
api_id = 'api id'
api_hash = 'api hash'
bot_token = 'bot token'

# Channels to monitor
channels_to_monitor = ['chyste_nebo', 'vseok450','AerisRimor','buchanskahromada','kyivmonitoring1']

# Regex patterns for detecting mentions of cities
words_sets = {
    "Set 1": {
        "Ірп": re.compile(r'\bІрп\w*\b', re.IGNORECASE),
        "Буч": re.compile(r'\bБуч\w*\b', re.IGNORECASE),
        "Гостом": re.compile(r'\bГостом\w*\b', re.IGNORECASE),
        "Коцюбин": re.compile(r'\bКоцюбин\w*\b', re.IGNORECASE),
        "Ворзел": re.compile(r'\bВорзел\w*\b', re.IGNORECASE),
    },
    "Set 2": {
        "Троє": re.compile(r'\bТроє\w*\b', re.IGNORECASE),
        "Погреб": re.compile(r'\bПогреб\w*\b', re.IGNORECASE),
        "Зазим": re.compile(r'\bЗазим\w*\b', re.IGNORECASE),
        "Осещин": re.compile(r'\bОсещин\w*\b', re.IGNORECASE),
        "Оболон": re.compile(r'\bОболон\w*\b', re.IGNORECASE),
        "Бровар": re.compile(r'\bБровар\w*\b', re.IGNORECASE),
        "Воскресен": re.compile(r'\bВоскресен\w*\b', re.IGNORECASE),
        "Деснянськ": re.compile(r'\bДеснянськ\w*\b', re.IGNORECASE),
        "Лісов": re.compile(r'\bЛісов\w*\b', re.IGNORECASE),
    },
}
selected_set = "Set 1"  # Default set
regex_patterns = words_sets[selected_set]  # Default to Set 1

# File to store user configurations
USER_CONFIG_FILE = 'user_configs.json'

def load_user_configs():
    if os.path.exists(USER_CONFIG_FILE):
        with open(USER_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_configs(configs):
    with open(USER_CONFIG_FILE, 'w') as f:
        json.dump(configs, f)

# Global dictionary to hold user configurations (chat_id and selected set)
user_configs = load_user_configs()

# ---------------------- BOT SETUP ----------------------
# Command to register a user and set default configuration
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_configs
    user_chat_id = str(update.effective_chat.id)
    # If new user, set default configuration ("Set 1")
    if user_chat_id not in user_configs:
        user_configs[user_chat_id] = "Set 1"
        save_user_configs(user_configs)
    await update.message.reply_text("✅ Notifications will be sent here when a keyword is detected.")

# Function to send a notification using the bot.
async def send_notification(text: str, application, chat_id: int):
    await application.bot.send_message(chat_id=chat_id, text=text)

# Command to display location options via inline keyboard
async def set_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Set 1 Ірпінь", callback_data="Set 1")],     # callback_data will be aviable in telegram.CallbackQuery.data.
        [InlineKeyboardButton("Set 2 Троєщина", callback_data="Set 2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔹 Select the location you want to monitor:", reply_markup=reply_markup)

# Handler for inline keyboard button press to update user's location choice
async def select_word_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_configs

    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    selected_set = query.data  # The chosen set from the button
    # Update this user's configuration in the JSON
    user_chat_id = str(query.message.chat.id)
    user_configs[user_chat_id] = selected_set
    save_user_configs(user_configs)

    await query.edit_message_text(text=f"✅ You have selected **{selected_set}**. The bot will now monitor for this area.")

# Helper function to notify all registered users
async def notify_all_users(message: str, application):
    for user_id in user_configs:
        try:
            await send_notification(message, application, int(user_id))
        except Exception as e:
            print(f"Error sending notification to user {user_id}: {e}")

# ---------------------- MAIN FUNCTION ----------------------
async def main():
    global telethon_client, user_configs

    #Initialize the Telegram bot application
    application = ApplicationBuilder().token(bot_token).build()

    #Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("location", set_words))
    application.add_handler(CallbackQueryHandler(select_word_set))


    #Ensure no webhook is active (prevents conflicts)
    async with application.bot as bot:
        await bot.delete_webhook(drop_pending_updates=True)

    #Start the bot manually (instead of using run_polling)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(poll_interval=30.0,timeout=120)  # Manually start polling

    #Initialize and start the Telethon client
    telethon_client = TelegramClient('session_name', api_id, api_hash)
    await telethon_client.start()
    print("✅ Telethon client started!")

    #Notify all users that the bot is active again
    await notify_all_users("✅ Bot is now active again.", application)

    #Define the Telethon event handler
    @telethon_client.on(events.NewMessage(chats=channels_to_monitor))
    async def telethon_handler(event):
        message_text = event.raw_text
        channel_title = event.chat.title if event.chat and hasattr(event.chat, 'title') else "Unknown Channel"

        # Iterate through each word set and check if the message matches any keyword.
        for set_name, patterns in words_sets.items():
            match_found = False
            match_key = None
            for key, pattern in patterns.items():
                if pattern.search(message_text):
                    match_found = True
                    match_key = key
                    break
            # If a match is found for this set, notify all users who have selected this set.
            if match_found:
                for user_id, user_set in user_configs.items():
                    if user_set == set_name:
                        notification_text = f"⚠️ Keyword '{match_key}' found in '{channel_title}':\n\n{message_text}"
                        try:
                            await send_notification(notification_text, application, int(user_id))
                        except Exception as e:
                            print(f"Error sending message to user {user_id}: {e}")

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