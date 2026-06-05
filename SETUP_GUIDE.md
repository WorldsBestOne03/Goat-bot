# 🐐 GOAT Bot — Setup Guide

## What You Need
- A free **Discord Developer** account
- A free **Anthropic API** account (claude.ai/api)
- A free **Railway** account to host it 24/7

---

## Step 1 — Create the Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **"New Application"** → name it `GOAT Bot`
3. Go to the **Bot** tab → Click **"Add Bot"**
4. Under **Privileged Gateway Intents**, enable:
   - ✅ Message Content Intent
5. Click **"Reset Token"** → Copy your **Bot Token** (save it!)
6. Go to **OAuth2 → URL Generator**:
   - Scopes: ✅ `bot` + ✅ `applications.commands`
   - Bot Permissions: ✅ `Send Messages` + ✅ `Use Slash Commands`
7. Copy the generated URL → Open it → Invite bot to your server

---

## Step 2 — Get Your Anthropic API Key

1. Go to https://console.anthropic.com
2. Create an account (free tier works)
3. Go to **API Keys** → Create a new key → Copy it

---

## Step 3 — Host on Railway (Free, 24/7)

1. Go to https://railway.app → Sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Push these files to a GitHub repo:
   - `goat_bot.py`
   - `requirements.txt`
4. In Railway, go to your project → **Variables** tab
5. Add these two environment variables:
   ```
   DISCORD_TOKEN = your_discord_bot_token
   ANTHROPIC_API_KEY = your_anthropic_api_key
   ```
6. Railway auto-detects Python and runs it — bot goes live!

---

## Step 4 — Test It in Discord

Type these slash commands in your server:

| Command | What it does |
|---|---|
| `/rank Drake` | Full breakdown + GOAT/Icon/Legend verdict |
| `/rank Whitney Houston` | Same for any artist |
| `/compare Jay-Z Nas` | Head-to-head with individual verdicts |
| `/help` | Shows all commands |

---

## Tier Definitions (Baked Into the Bot)

| Tier | Meaning |
|---|---|
| 🐐 GOAT | Changed the culture PERMANENTLY — Elvis, Whitney, MJ level |
| ⭐ ICON | Defined their era — the face of their genre/moment |
| 🏆 LEGEND | Highly respected, hall-of-fame level |

---

## What the Bot Pulls on Every Artist

- 📀 Albums & estimated sales
- 🏆 Grammy count + major awards
- 📊 Billboard chart history
- 🌍 Cultural impact & milestones
- 💰 Tours, business ventures, legacy
- 🎯 Final verdict with the reasoning to back it up

---

## Local Testing (Optional)

```bash
pip install discord.py anthropic python-dotenv
python goat_bot.py
```

Create a `.env` file in the same folder:
```
DISCORD_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_key_here
```
