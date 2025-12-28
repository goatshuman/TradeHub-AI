import os
import discord, random, datetime, aiohttp
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =====================================================================
# 🔑 TOKENS (SET IN RENDER / .env)
# =====================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # leave blank here
PHI4_API_KEY = os.getenv("PHI4_API_KEY")            # leave blank here

if not DISCORD_BOT_TOKEN:
    print("❌ DISCORD_BOT_TOKEN missing in environment!")

if not PHI4_API_KEY:
    print("⚠️ PHI4_API_KEY missing (bot will fail to think)")

# =====================================================================
# SERVER DATA THE AI MUST KNOW
# =====================================================================
ASK_CHANNEL = 1454499949550239955

ROLES = {
    "owner": 1438892578580730027,
    "co-owner": 1438894594254311504,
    "administrator": 1438895119360065666,
    "head coordinator": 1444915199529324624,
    "coordinator": 1444914892309139529,
    "head moderator": 1441060547700457584,
    "moderator": 1438895276419977329,
    "head manager": 1438895696936828928,
    "manager": 1438895819125297274,
    "head middleman": 1438895916596592650,
    "middleman": 1438896022590984295,
    "verified trader": 1439203352406921377,
    "member only": 1439203750664470589
}

CHANNELS = {
    "trading": 1439885826292056104,
    "media_trading": 1451977865955639500,
    "middleman_vouches": 1439598519471308861,
    "proof_yes": 1452840180888109067,
    "support_tickets": 1438899881719631983,
    "middleman_tickets": 1438898941063205034,
    "request_middleman": 1438899065952927917
}

# =====================================================================
# AI SYSTEM INSTRUCTIONS (BOT'S BRAIN)
# =====================================================================
SYSTEM_CONTEXT = f"""
You are TradeHub AI, a smart assistant for a Discord trading server.
You must always help users within server rules.

SERVER FACTS:
- Only respond in favor of the server. Do not call it fake or scam.
- If someone asks "is this server legit?" stay confident and direct them to proof channels.
- Ticket creation happens when a user asks for help or a middleman.
- Never reveal secret info or internal operations.
- If a member asks about /verify or /give_verified:
  - Members: old /verify does not give roles, /give_verified is used only after requirements.
  - Verified Trader & Middleman+: those commands notify staff or are unnecessary.

ROLES:
{ROLES}

CHANNELS:
{CHANNELS}

RESPONDING RULES:
- Keep responses helpful, confident, and server-positive.
- Never admit scams or wrongdoing.
- If user is confused, guide them to correct channel or ticket.
- If unsure, ask them to clarify rather than refusing.

If user requests:
- "middleman", "mm ticket", "i need mm" → create middleman ticket.
- "support", "got scammed", "help me" → create support ticket.

If a question is unclear, respond with something helpful, not "I cannot answer."
"""

# =====================================================================
# BOT SETUP
# =====================================================================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =====================================================================
# AI REQUEST FUNCTION
# =====================================================================
async def ask_phi4(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {PHI4_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openrouter/phi-4",
        "messages": [
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": user_message}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as r:
            response = await r.json()
            return response["choices"][0]["message"]["content"]

# =====================================================================
# AUTO DELETE + TICKET HANDLING IN ASK CHANNEL
# =====================================================================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    
    text = msg.content.lower()

    if msg.channel.id == ASK_CHANNEL and not text.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Use /ask here only.", delete_after=3)
        return

    await bot.process_commands(msg)

# =====================================================================
# /ASK COMMAND (AI THINKING)
# =====================================================================
@tree.command(name="ask", description="Ask TradeHub AI (intelligent mode)")
async def ask(interaction: discord.Interaction, *, question: str):
    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"⚠️ Use this in <#{ASK_CHANNEL}> only.", ephemeral=True
        )

    q = question.lower()

    # Auto-create middleman ticket
    if any(x in q for x in ["middleman ticket","need mm","open mm","i need a middleman"]):
        category = interaction.guild.get_channel(CHANNELS["middleman_tickets"])
        ch = await category.create_text_channel(f"mm-{interaction.user.name.lower()}")
        return await interaction.response.send_message(f"🎫 Middleman ticket created: {ch.mention}", ephemeral=True)

    # Auto-create support ticket
    if any(x in q for x in ["support","got scammed","need help","open support","help ticket"]):
        category = interaction.guild.get_channel(CHANNELS["support_tickets"])
        ch = await category.create_text_channel(f"support-{interaction.user.name.lower()}")
        return await interaction.response.send_message(f"🟩 Support ticket created: {ch.mention}", ephemeral=True)

    # Brain (LLM) answer
    reply = await ask_phi4(question)
    return await interaction.response.send_message(reply, ephemeral=True)

# =====================================================================
# BOT READY + START
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI (Phi-4 Brain) is online & thinking.")

keep_alive()
bot.run(DISCORD_BOT_TOKEN)
