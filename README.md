# DroneAlert Telegram Bot 🛡️
Unfortunately, drone attacks on Ukrainian territory occur daily. In my experience, Telegram monitoring channels are the most reliable sources of timely information during such attacks.

Having immediate access to a proper shelter is a luxury—most people simply seek safety in the most secure area of their homes. However, drone attacks frequently last hours, often throughout the night, making it exhausting to manually monitor these Telegram channels continuously.

To help my family and myself manage this stress and maintain alertness efficiently, I built this Telegram bot.

It won't create an impenetrable shield, but it does remove the need to constantly watch monitoring channels personally. When your selected locations appear in monitored Telegram channels, the bot sends an immediate alert—letting you know that danger is close by.

If you'd like to create a similar bot for yourself, feel free to do so. I hope my code provides a helpful starting point.

Stay safe. 🌻🇺🇦

# 🔹 Project Overview
This bot tracks real-time messages from selected Telegram channels, scanning them for mentions of user-specified locations. Upon detecting predefined keywords, it immediately sends alerts to users, keeping them promptly informed of relevant drone activity.

# 🔹 Key Features
Real-time monitoring of Telegram channels via Telethon.
Webhook-based notifications powered by python-telegram-bot, FastAPI, and Uvicorn.
Dynamic user preferences with customizable location monitoring (persisted in JSON format).
Designed for deployment: Tested locally and deployed on AWS Lightsail with HTTPS webhook enabled (using a reverse proxy via Caddy and Let’s Encrypt SSL certificates).
# 🔹 Tech Stack
Telethon for interacting with Telegram API.
Python-Telegram-Bot for bot interaction handling.
FastAPI + Uvicorn for lightweight webhook server.
Caddy as a reverse proxy and automated TLS certificate management.
# 🔹 Deployment and Infrastructure
Deployed on AWS Lightsail instance (Ubuntu-based), using Cloudflare for domain management and Caddy for automatic HTTPS and reverse proxy handling.
