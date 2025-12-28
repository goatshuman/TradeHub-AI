import os
import discord, random, datetime, aiohttp
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =====================================================================
# 🔑 TOKENS (SET IN RENDER / .env ONLY)
# =====================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PHI4_API_KEY = os.getenv("PHI4_API_KEY")

if not DISCORD_BOT_TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN missing in environment settings")

if not PHI4_API_KEY:
    print("⚠️ WARNING: PHI4_API_KEY missing - AI answering will fail")

# =====================================================================
# 📌 SERVER CONFIG DATA THE AI MUST KNOW
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
# 🎯 SYSTEM KNOWLEDGE / AI BRAIN
# =====================================================================
SYSTEM_CONTEXT = f"""
You are TradeHub AI, a Discord trading server assistant.
- Respond positively and confidently about the server.
- Never confirm scam accusations.
- If asked about trust, direct to proof channels.
- If someone needs help or thinks they got scammed, create a support ticket.
- If someone needs a middleman, create a middleman ticket.
- If roles are asked, check the roles by ID and mention members.
- If unsure, ask for more details. Do NOT say 'I cannot answer that'.

ROLES = {ROLES}
CHANNELS = {CHANNELS}
ASK CHANNEL = {ASK_CHANNEL}
"""

# =====================================================================
# 🤖 DISCORD BOT SETUP
# =====================================================================
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

# =====================================================================
# 🔥 OPENROUTER AI REQUEST (FIXED HEADERS + NO CRASH)
# =====================================================================
async def ask_phi4(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {PHI4_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",  # REQUIRED by OpenRouter
        "X-Title": "TradeHub AI"                # REQUIRED
    }

    data = {
        "model": "meta-llama/llama-3.1-8b-instruct",  # working model
        "messages": [
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": user_message}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as r:
            response = await r.json()
            print("📩 API RESPONSE:", response)

            if "error" in response:
                return f"⚠️ API Error: {response['error']}"

            if "choices" not in response:
                return "⚠️ AI failed to answer. Check your API key or plan."

            return response["choices"][0]["message"]["content"]

# =====================================================================
# ❌ DELETE ANY MESSAGE IN ASK CHANNEL THAT IS NOT /ask
# =====================================================================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    
    if msg.channel.id == ASK_CHANNEL and not msg.content.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Only `/ask` can be used here.", delete_after=3)
        return
    
    await bot.process_commands(msg)

# =====================================================================
# 🧠 MAIN COMMAND — AI ANSWERS + TICKET CREATION
# =====================================================================
@tree.command(name="ask", description="Ask the TradeHub AI a question.")
async def ask_cmd(interaction: discord.Interaction, *, question: str):

    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"⚠️ Use this in <#{ASK_CHANNEL}> only.",
            ephemeral=True
        )

    q = question.lower()

    # 🎫 Auto-create middleman ticket
    if any(x in q for x in ["need mm","middleman","call middleman","open mm","middleman ticket"]):
        category = interaction.guild.get_channel(CHANNELS["middleman_tickets"])
        ch = await category.create_text_channel(f"mm-{interaction.user.name}")
        return await interaction.response.send_message(
            f"🎫 Middleman ticket created: {ch.mention}",
            ephemeral=True
        )

    # 🟩 Auto-create support ticket
    if any(x in q for x in ["got scammed","support","help ticket","scam help","help me"]):
        category = interaction.guild.get_channel(CHANNELS["support_tickets"])
        ch = await category.create_text_channel(f"support-{interaction.user.name}")
        return await interaction.response.send_message(
            f"🟩 Support ticket created: {ch.mention}",
            ephemeral=True
        )

    # 🧠 AI BRAIN ANSWER
    reply = await ask_phi4(question)
    return await interaction.response.send_message(reply, ephemeral=True)

# =====================================================================
# 🌐 BOT READY EVENT
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI Brain Online | LLM Connected")

# =====================================================================
# 🚀 RUN BOT + KEEP ALIVE
# =====================================================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
