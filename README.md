# DroneAlert Telegram Bot 🛡️
Unfortunately, drone attacks on Ukrainian territory occur daily. In my experience, Telegram monitoring channels are the most reliable sources of timely information during such attacks.

Having immediate access to a proper shelter is a luxury—most people simply seek safety in the most secure area of their homes. However, drone attacks frequently last hours, often throughout the night, making it exhausting to manually monitor these Telegram channels continuously.

To help my family and myself manage this stress and maintain alertness efficiently, I built this Telegram bot.

It won't create an impenetrable shield, but it does remove the need to constantly watch monitoring channels personally. When your selected locations appear in monitored Telegram channels, the bot sends an immediate alert—letting you know that danger is close by.

If you'd like to create a similar bot for yourself, feel free to do so. I hope my code provides a helpful starting point.

Stay safe. 🌻🇺🇦

# Project Overview
This bot tracks real-time messages from selected Telegram channels, scanning them for mentions of user-specified locations. Upon detecting predefined keywords, it immediately sends alerts to users, keeping them promptly informed of relevant drone activity.

# Key Features
+ Real-time monitoring of Telegram channels via Telethon.
+ Webhook-based notifications. Tested using polling too.
+ Dynamic user preferences with customizable location monitoring (persisted in JSON format).
+ Designed for deployment: Tested locally and deployed on AWS Lightsail with HTTPS webhook enabled (using a reverse proxy via Caddy and Let’s Encrypt SSL certificates).
# Tech Stack
+ `telethon` for interacting with Telegram API.
+ `python-telegram-bot` for bot interaction handling.
+ FastAPI + Uvicorn for lightweight webhook server.
+ Caddy as a reverse proxy and automated TLS certificate management.
# Deployment and Infrastructure
Deployed on AWS Lightsail instance (Ubuntu-based), using Cloudflare for domain management and Caddy for automatic HTTPS and reverse proxy handling.

# 🚧 Development Steps
### 1. Identify the problem and a way to solve it 
Realized that monitoring multiple Telegram channels continuously is impractical.

Creating an automated Telegram bot to monitor selected channels is a solution.

How? By alerting users immediately if certain keywords (e.g., names of local towns or districts) appear, signaling potential danger nearby.
### 2. Technologies Chosen
Researched Telegram API and relevant libraries. Decided on the following tech stack:
+ Python
+ `telethon` (to be able to read messages from monitoring channels)
+ `python-telegram-bot` library for sending messages and managing user interaction.
### 3. Telegram APIs
Received api_id and api_hash for [Telegram client](https://core.telegram.org/api/obtaining_api_id).

Via [@BotFather](https://t.me/botfather) created my bot and received bot_token as its unique identifier.

> [!NOTE]
> Here is my bot, by the way, [@irpinalert_bot](https://t.me/irpinalert_bot). I start it almost every evening only for the nighttime (GMT+2).

### 4. Initial Bot Prototype 
Developed the bot initially using polling (simpler implementation, more information).

Set up Telegram handlers for bot command (`/start` command).

Created my own Telegram channel for testing notification.

Bot was able to handle only one user for now.

### 5. Considering Webhook approach
Polling approach worked well, but the bot asked for updates so frequently, that it looked like spamming Telegram API with requests. 
> getUpdates is a pull mechanism
> 
> setWebhook is push

I also had in mind, that my local computer will not do as a server for bot working at night (or if there is a problem with electricity in my region due to russian attacks). 
So I choosed to relocate to cloud - AWS Lightsail.

Setting a webhook on a new server was quite challenging, as it requires a lot of details to consider. But I did it anyway :smile:
### 6. Refactor to Webhook and Cloud
Official [webhook guide](https://core.telegram.org/bots/webhooks) helped for the start.

Tech stack:
+ Ngrok for testing
+ FastAPI + Uvicorn for webserver setup
+ Caddy for TLS certificates and reverse proxy
   
Researched and tested webhook setup using Ngrok locally to understand webhook mechanics. 

Created an Ubuntu instance on AWS Lightsail for reliable 24/7 deployment. Configured a static IPv4 address (IPv6 is not supported for Telegram webhooks).

Installed Python packages in a virtual environment to maintain clean dependency management.

Registered a domain name via Cloudflare and used it as DNS provider. 

Installed and configured Caddy to automatically manage SSL certificates through Let's Encrypt and work as reverse proxy.

Integrated FastAPI server on Lightsail to receive webhook updates.

Debugged webhook communication between Telegram, Cloudflare (DNS), and AWS Lightsail server. Enabled 'Full' encryption mode in CloudFlare (not 'Flexible').

- [X] Finally, ensured stable HTTPS connection end-to-end.

### 7. Implemented User Interaction

Added commands (/start, /location) to let users select their desired monitoring locations.

Stored user preferences and chats ids in a JSON file, ensuring persistence between server restarts.

New features were implemented firstly with polling mechanism for ease of debugging.

### 8. Deployment and Monitoring

New features added to webhook version.

Managed bot lifecycle with `tmux` on AWS Lightsail to keep bot running after SSH logout.

Monitored memory and resource usage on AWS Lightsail to ensure stable performance. Used SWAP apace as Lightsails free instance has little RAM capacity.

- [X]  Confirmed successful notification delivery when target words appeared in monitored channels.

## 📌 **Code Versions**

| Step | Description | 
|------|-------------|
| Initial bot script (polling) | [`1_dronealertbot_polling.py`](scripts/1_dronealertbot_polling.py) 
| Initial bot script (webhook) | [`2_dronealertbot_webhook.py`](scripts/2_dronealertbot_webhook.py) 
| Multiple users and location choice added (polling) | [`3_dronealertbot_polling_new_features.py`](scripts/3_dronealertbot_polling_new_features.py) 
| Multiple users and location choice added (webhook) | [`4_dronealertbot_webhook_new_features.py`](scripts/4_dronealertbot_webhook_new_features.py) 




