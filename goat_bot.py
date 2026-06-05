"""
🏆 GOAT BOT — Discord Artist Ranking Bot
=========================================
Ranks artists as GOAT, Icon, or Legend using AI + web search.

TIER DEFINITIONS:
  🐐 GOAT   = Changed the culture PERMANENTLY (MJ, Elvis, Whitney level)
  ⭐ ICON   = Defined their era — the face of their genre/moment
  🏆 LEGEND = Highly respected, hall-of-fame level, but below Icon

SETUP INSTRUCTIONS:
-------------------
1. Install dependencies:
      pip install discord.py anthropic python-dotenv

2. Create a .env file in the same folder with:
      DISCORD_TOKEN=your_discord_bot_token_here
      ANTHROPIC_API_KEY=your_anthropic_api_key_here

3. Create your Discord bot at https://discord.com/developers/applications
      - Enable "Message Content Intent" under Bot settings
      - Invite the bot with scopes: bot + applications.commands

4. Host for free on Railway (railway.app) or Render (render.com)
      - Push this file + requirements.txt + .env to a repo
      - Railway/Render will keep it running 24/7

5. Run locally to test:
      python goat_bot.py

COMMANDS:
----------
  /rank [artist]     — Full breakdown + GOAT/Icon/Legend verdict
  /compare [a] vs [b] — Compare two artists side by side
  /help              — Show bot commands

"""

import discord
from discord import app_commands
from discord.ext import commands
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ── Bot setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Tier definitions sent to Claude ──────────────────────────────────────────
TIER_SYSTEM_PROMPT = """
You are GOAT Bot — the ultimate music artist ranking judge for a Discord server.

Your job is to research an artist's full career and classify them into one of three tiers:

🐐 GOAT — Changed the culture PERMANENTLY. Their influence never dies. 
          Examples: Michael Jordan (sports), Elvis Presley, Whitney Houston, Michael Jackson, 
          Prince, The Beatles. These are once-in-a-generation figures who didn't just succeed 
          — they fundamentally altered what was possible in their field.

⭐ ICON  — Defined their era. The face of their genre or moment. 
           Massive commercial success, cultural relevance, legendary status — but their 
           influence is more tied to a specific era or genre rather than changing the entire 
           game forever.

🏆 LEGEND — Highly respected, Hall-of-Fame level. Sustained excellence, major awards, 
             devoted fanbase, clear legacy — but operating below the Icon level in terms 
             of crossover cultural impact.

RESPONSE FORMAT — Always respond in this exact structure:

**🎤 [ARTIST NAME] — Career Breakdown**

**📀 Discography & Sales**
[Key albums, total estimated sales, notable chart performances]

**🏆 Awards & Recognition**
[Grammy count, other major awards, nominations, records broken]

**📊 Chart History**
[Billboard Hot 100 peaks, album chart performance, number ones]

**🌍 Cultural Impact**
[How they moved the culture, moments that defined them, influence on other artists]

**💰 Business & Legacy**
[Tours, earnings, brand deals, business ventures, posthumous legacy if applicable]

**🎯 Tier Verdict**
[ONE of: 🐐 GOAT | ⭐ ICON | 🏆 LEGEND]

**📋 The Reasoning**
[3-5 sentences explaining exactly WHY they landed in that tier. Be direct and cite specifics.]

Keep the tone confident, conversational, and debate-ready. 
Write like someone who really knows music and isn't afraid to take a stance.
Use web search to get accurate, up-to-date career stats before making your verdict.
"""

COMPARE_SYSTEM_PROMPT = """
You are GOAT Bot — the ultimate music artist ranking judge for a Discord server.

Your job is to compare TWO artists head-to-head and rank each one.

TIERS:
🐐 GOAT   — Changed the culture PERMANENTLY (Elvis, Whitney, MJ level)
⭐ ICON   — Defined their era and genre
🏆 LEGEND — Hall-of-fame level, highly respected

RESPONSE FORMAT:

**⚔️ HEAD-TO-HEAD: [ARTIST 1] vs [ARTIST 2]**

---

**[ARTIST 1]**
• Sales & Charts: [key stats]
• Awards: [key stats]  
• Cultural Impact: [brief]
• Tier: [🐐 GOAT / ⭐ ICON / 🏆 LEGEND]

---

**[ARTIST 2]**
• Sales & Charts: [key stats]
• Awards: [key stats]
• Cultural Impact: [brief]
• Tier: [🐐 GOAT / ⭐ ICON / 🏆 LEGEND]

---

**🔥 The Verdict**
[Who wins the debate and why — be direct, cite the receipts]

Use web search to pull accurate career stats before making your verdict.
Keep it debate-ready and confident.
"""


# ── Helper: call Claude with web search ──────────────────────────────────────
def ask_claude(system_prompt: str, user_message: str) -> str:
    """Call Claude Sonnet with web search enabled and return the response text."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system_prompt,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_message}],
    )

    # Collect all text blocks from the response
    full_text = ""
    for block in response.content:
        if block.type == "text":
            full_text += block.text

    return full_text.strip() if full_text else "⚠️ Couldn't generate a response. Try again."


# ── Split long messages for Discord's 2000 char limit ────────────────────────
def split_message(text: str, limit: int = 1900) -> list[str]:
    """Split a long string into chunks that fit Discord's message limit."""
    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    chunks.append(text)
    return chunks


# ── Events ────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/rank [artist] 🐐"
        )
    )
    print(f"✅ GOAT Bot is online as {bot.user}")
    print(f"   Servers: {len(bot.guilds)}")


# ── /rank command ─────────────────────────────────────────────────────────────
@bot.tree.command(name="rank", description="Get a full career breakdown + GOAT/Icon/Legend verdict")
@app_commands.describe(artist="The artist you want ranked (e.g. Drake, Beyoncé, Tupac)")
async def rank(interaction: discord.Interaction, artist: str):
    await interaction.response.defer(thinking=True)  # Shows "Bot is thinking..."

    try:
        result = ask_claude(
            TIER_SYSTEM_PROMPT,
            f"Research and rank this artist: {artist}"
        )

        chunks = split_message(result)
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)

    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Something went wrong ranking **{artist}**. Try again in a moment.\n`Error: {e}`"
        )


# ── /compare command ──────────────────────────────────────────────────────────
@bot.tree.command(name="compare", description="Compare two artists head-to-head")
@app_commands.describe(
    artist1="First artist",
    artist2="Second artist"
)
async def compare(interaction: discord.Interaction, artist1: str, artist2: str):
    await interaction.response.defer(thinking=True)

    try:
        result = ask_claude(
            COMPARE_SYSTEM_PROMPT,
            f"Compare these two artists head-to-head: {artist1} vs {artist2}"
        )

        chunks = split_message(result)
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)

    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Something went wrong comparing **{artist1}** vs **{artist2}**.\n`Error: {e}`"
        )


# ── /help command ─────────────────────────────────────────────────────────────
@bot.tree.command(name="help", description="Show all GOAT Bot commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏆 GOAT Bot — Commands",
        description="Settle the debate with receipts.",
        color=0xFFD700
    )
    embed.add_field(
        name="🐐 `/rank [artist]`",
        value="Full career breakdown + GOAT / Icon / Legend verdict\n*Example: `/rank Kendrick Lamar`*",
        inline=False
    )
    embed.add_field(
        name="⚔️ `/compare [artist1] [artist2]`",
        value="Head-to-head comparison with individual verdicts\n*Example: `/compare Jay-Z Nas`*",
        inline=False
    )
    embed.add_field(
        name="📊 Tier Definitions",
        value=(
            "🐐 **GOAT** — Changed the culture PERMANENTLY\n"
            "⭐ **ICON** — Defined their era\n"
            "🏆 **LEGEND** — Hall-of-fame level respected"
        ),
        inline=False
    )
    embed.set_footer(text="GOAT Bot powered by Claude AI + Web Search")
    await interaction.response.send_message(embed=embed)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
