import os
import random
import discord
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

ASK_CHANNEL = 1454499949550239955

# CHANNEL REFERENCES
TRADE = "<#1439885826292056104>"
TRADE_MEDIA = "<#1451977865955639500>"
SUPPORT = "<#1438900168006045907>"
REQUEST_MM = "<#1438899065952927917>"
PROOF = "<#1452840180888109067>"
VOUCHES = "<#1439598519471308861>"
YES_PROOF = "<#1452840180888109067>"
NO_CHANNEL = "<#1452840053125546194>"

# =======================
# REPLY BANKS (CHANNEL INCLUDED)
# =======================

SCAM_SUPPORT = [
    f"🚨 If you think something is wrong or scam related, open a support ticket here: {SUPPORT}",
    f"⚠️ Worried about a scam? Support will check everything. Open a ticket here: {SUPPORT}",
    f"🛟 Don't panic. Just go to {SUPPORT} and staff will guide you.",
    f"📌 If someone is acting suspicious, open a support ticket now: {SUPPORT}.",
    f"🚑 Support will verify screenshots and messages. Open here: {SUPPORT}.",
]

MIDDLEMAN = [
    f"🤝 Need a safe trade? Request a middleman here: {REQUEST_MM}",
    f"📩 To start a safe trade with a middleman, go here: {REQUEST_MM}",
    f"🛡 Want protection during trade? Request an MM here: {REQUEST_MM}",
    f"✨ Middleman helps both sides. Start here: {REQUEST_MM}",
]

LEGIT_TRUST = [
    f"📁 This server is 100% legit dont worry: {PROOF}",
    f"📌 Public vouches are listed here: {VOUCHES}",
    f"📝 Everything is transparent. Proof: {PROOF} | Vouches: {VOUCHES}",
    f"📂 Need reassurance? Check proof here: {PROOF}",
    f"🔍 Confirmations are public: {VOUCHES}",
]

TRADE_REPLIES = [
    f"💹 Want to trade? Use {TRADE}",
    f"🛒 Image/video based trades can go here: {TRADE_MEDIA}",
    f"📍 Start trading conversations in: {TRADE}",
    f"📁 Media proof trading is done in: {TRADE_MEDIA}",
    f"🪙 Trading section available here: {TRADE}",
]

GREETINGS = [
    "👋 Hey! How can I help you today?",
    "👀 I'm here. What do you need?",
    "✨ Hello! Ask anything related to trading or support.",
    "⚡ Yo! What do you need help with?",
]

UNKNOWN = [
    "🤔 I need a bit more detail. Try asking again clearly.",
    "💬 I'm here, explain a little more.",
    "📌 Ask with a few more words so I can respond properly.",
]

# =======================
# BOT SETUP
# =======================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =======================
# DELETE NON-COMMAND MESSAGES IN /ask CHANNEL
# =======================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    if msg.channel.id == ASK_CHANNEL and not msg.content.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Only `/ask` works here.", delete_after=2)
        return
    await bot.process_commands(msg)

# =======================
# CLASSIFICATION (PRIORITY ORDER)
# Scam > Middleman > Legit/Proof > Trade > Greetings > Unknown
# =======================
def classify(text):
    t = text.lower()

    if any(x in t for x in ["scam","scammed","fake","doubt","stole","problem","issue","help","scammer"]):
        return random.choice(SCAM_SUPPORT)

    if any(x in t for x in ["middleman","mm","secure","hold","protection"]):
        return random.choice(MIDDLEMAN)

    if any(x in t for x in ["legit","real","trust","verified","proof","confirmations"]):
        return random.choice(LEGIT_TRUST)

    if any(x in t for x in ["trade","buy","sell","deal","offer"]):
        return random.choice(TRADE_REPLIES)

    if any(x in t for x in ["hi","hello","yo","hey","hola","sup"]):
        return random.choice(GREETINGS)

    return random.choice(UNKNOWN)

# =======================
# /ASK COMMAND
# =======================
@tree.command(name="ask", description="Ask TradeHub.AI something about the server.")
async def ask(interaction: discord.Interaction, *, question: str):
    await interaction.response.defer(ephemeral=True)

    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.followup.send(
            f"⚠️ Use `/ask` only in <#{ASK_CHANNEL}>.",
            ephemeral=True
        )

    response = classify(question)
    await interaction.followup.send(response, ephemeral=True)

# =======================
# READY
# =======================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI Active — Scripted Reply System ON")

keep_alive()
bot.run(DISCORD_BOT_TOKEN)
