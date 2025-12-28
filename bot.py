import os
import discord, random, datetime, aiohttp
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =====================================================================
# 🔑 TOKENS (SET IN RENDER / .env ONLY - DO NOT PUT IN CODE)
# =====================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PHI4_API_KEY = os.getenv("PHI4_API_KEY")

if not DISCORD_BOT_TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN missing in Render/.env")

if not PHI4_API_KEY:
    print("⚠️ WARNING: PHI4_API_KEY missing - AI responses may fail")

# =====================================================================
# SERVER CONFIG DATA (AI WILL USE THIS TO THINK)
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
# 🎯 SYSTEM MESSAGE (AI BRAIN INSTRUCTIONS)
# =====================================================================
SYSTEM_CONTEXT = f"""
You are TradeHub AI, an assistant for a trading Discord server.
Your responses must:
- Support the server.
- Never agree with scam accusations.
- Direct users to proof channels when asked about trust: {CHANNELS['middleman_vouches']}, {CHANNELS['proof_yes']}
- Create tickets when someone asks for help, scam support, or middleman.
- Treat 'member only' role as the lowest level.
- If unsure: ask for clarification, DO NOT say 'I cannot answer'.

ROLES:
{ROLES}

CHANNELS:
{CHANNELS}
"""

# =====================================================================
# 🔥 BOT BASE
# =====================================================================
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

# =====================================================================
# 🤖 AI REQUEST FUNCTION (FIXED, NO MORE "choices" ERROR)
# =====================================================================
async def ask_phi4(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {PHI4_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": user_message}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as r:
            response = await r.json()
            print("📩 API RESPONSE:", response)  # log for debugging

            # Error handling
            if "error" in response:
                return "⚠️ API error: " + str(response["error"])
            if "choices" not in response:
                return "⚠️ AI failed to answer. Check API key/model."

            return response["choices"][0]["message"]["content"]

# =====================================================================
# 💬 AUTO DELETE IN ASK CHANNEL
# =====================================================================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    if msg.channel.id == ASK_CHANNEL and not msg.content.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Only `/ask` is allowed here.", delete_after=3)
        return
    await bot.process_commands(msg)

# =====================================================================
# 💡 /ASK COMMAND (AI THINKING)
# =====================================================================
@tree.command(name="ask", description="Ask TradeHub AI (Brain Enabled)")
async def ask(interaction: discord.Interaction, *, question: str):
    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"⚠️ Use this command only in <#{ASK_CHANNEL}>.",
            ephemeral=True
        )

    q = question.lower()

    # 🎫 Middleman Ticket
    if any(x in q for x in ["middleman ticket","need mm","i need a middleman","call mm"]):
        category = interaction.guild.get_channel(CHANNELS["middleman_tickets"])
        ch = await category.create_text_channel(f"mm-{interaction.user.name.lower()}")
        return await interaction.response.send_message(f"🎫 Middleman ticket created: {ch.mention}", ephemeral=True)

    # 🟩 Support Ticket
    if any(x in q for x in ["support","got scammed","help ticket","i need help","open support"]):
        category = interaction.guild.get_channel(CHANNELS["support_tickets"])
        ch = await category.create_text_channel(f"support-{interaction.user.name.lower()}")
        return await interaction.response.send_message(f"🟩 Support ticket created: {ch.mention}", ephemeral=True)

    # 🧠 AI RESPONSE
    reply = await ask_phi4(question)
    return await interaction.response.send_message(reply, ephemeral=True)

# =====================================================================
# 🔛 BOT ONLINE
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI is online with brain mode enabled.")

# =====================================================================
# 🚀 RUN BOT
# =====================================================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
