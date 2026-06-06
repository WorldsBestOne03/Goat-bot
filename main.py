import discord
from discord import app_commands
from discord.ext import commands
import anthropic
import os

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = """
You are GOAT Bot — the ultimate cultural figure ranking judge for a Discord server.

Rank any artist, athlete, entertainer, or public figure into one of three tiers:

GOAT — Changed the culture PERMANENTLY. Once-in-a-generation. Examples: Michael Jackson, Elvis, Whitney Houston, Muhammad Ali, Michael Jordan.

ICON — Defined their era. The face of their genre or moment. Massive success and cultural relevance tied to a specific era.

LEGEND — Highly respected, hall-of-fame level. Sustained excellence and major achievements but below Icon level crossover impact.

When given a name, respond with this exact format:

**[NAME] — Career Breakdown**

**Albums/Work & Sales**
[key projects and numbers]

**Awards & Recognition**
[major awards, records broken]

**Chart & Stats History**
[peak chart positions, notable stats]

**Cultural Impact**
[how they moved the culture]

**Business & Legacy**
[tours, earnings, lasting impact]

**VERDICT: [GOAT / ICON / LEGEND]**

**Why:**
[3-4 sentences explaining the verdict with specific facts]

Be confident, direct, and debate-ready. Works for musicians, athletes, actors, anyone.
"""

def split_message(text, limit=1900):
    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    chunks.append(text)
    return chunks

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/goat [name] 🐐"
        )
    )
    print(f"GOAT Bot is online as {bot.user}")

@bot.tree.command(name="goat", description="Get a full career breakdown + GOAT/Icon/Legend verdict")
@app_commands.describe(name="Who do you want ranked? (artist, athlete, anyone)")
async def goat(interaction: discord.Interaction, name: str):
    await interaction.response.defer(thinking=True)
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Rank this person: {name}"}],
        )
        result = response.content[0].text
        chunks = split_message(result)
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)
    except Exception as e:
        await interaction.followup.send(f"Something went wrong ranking **{name}**. Try again.\nError: {e}")

@bot.tree.command(name="compare", description="Compare two people head to head")
@app_commands.describe(person1="First person", person2="Second person")
async def compare(interaction: discord.Interaction, person1: str, person2: str):
    await interaction.response.defer(thinking=True)
    try:
        prompt = f"Compare these two head to head and rank each one as GOAT, ICON, or LEGEND: {person1} vs {person2}. Give each their own breakdown then a final verdict on who wins the debate."
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.content[0].text
        chunks = split_message(result)
        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)
    except Exception as e:
        await interaction.followup.send(f"Something went wrong. Try again.\nError: {e}")

@bot.tree.command(name="goathelp", description="Show all GOAT Bot commands")
async def goathelp(interaction: discord.Interaction):
    embed = discord.Embed(
        title="GOAT Bot — Commands",
        description="Settle the debate with receipts.",
        color=0xFFD700
    )
    embed.add_field(name="/goat [name]", value="Full breakdown + GOAT/Icon/Legend verdict\nExample: /goat Beyonce", inline=False)
    embed.add_field(name="/compare [person1] [person2]", value="Head to head comparison\nExample: /compare LeBron Kobe", inline=False)
    embed.add_field(name="Tiers", value="🐐 GOAT = Changed culture permanently\n⭐ ICON = Defined their era\n🏆 LEGEND = Hall of fame respected", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(DISCORD_TOKEN)
