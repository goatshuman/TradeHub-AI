import os
import discord, aiohttp
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# ==========================================================
# tokens come from Render / .env (DO NOT PUT IN CODE)
# ==========================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PHI4_API_KEY = os.getenv("PHI4_API_KEY")

if not DISCORD_BOT_TOKEN:
    print("❌ Missing DISCORD_BOT_TOKEN in Render variables")
if not PHI4_API_KEY:
    print("❌ Missing PHI4_API_KEY in Render variables")

# ==========================================================
# server config
# ==========================================================
ASK_CHANNEL = 1454499949550239955

CHANNELS = {
    "trade": 1439885826292056104,
    "trade_media": 1451977865955639500,
    "proof_yes": 1452840180888109067,
    "vouches": 1439598519471308861,
    "support_cat": 1438899881719631983,
    "mm_cat": 1438898941063205034
}

# ==========================================================
# AI brain instructions
# ==========================================================
SYSTEM_CONTEXT = f"""
You are TradeHub AI. Always answer confidently.
Never say "I cannot answer". Never say "unsure".
If asked about trust → send them to proof: <#{CHANNELS['proof_yes']}>
If asked for vouches → <#{CHANNELS['vouches']}>
If needs middleman → open middleman ticket.
If thinks got scammed → open support ticket.
If asked about trading → <#{CHANNELS['trade']}> or <#{CHANNELS['trade_media']}>
"""

# ==========================================================
# bot base
# ==========================================================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ==========================================================
# AI request (NO COOKIE - FIXED HEADERS)
# ==========================================================
async def phi4(question):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {PHI4_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",     # REQUIRED
        "X-Title": "TradeHub AI"                   # REQUIRED
    }
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": question}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as res:
            response = await res.json()
            print("📩 API RESPONSE:", response)

            # If blocked → fail-safe reply
            if "choices" not in response:
                return "⚠️ AI is blocked right now, but I'm active. Ask again in a minute! 😊"

            return response["choices"][0]["message"]["content"]


# ==========================================================
# delete normal messages in /ask channel
# ==========================================================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    if msg.channel.id == ASK_CHANNEL and not msg.content.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Only `/ask` works here.", delete_after=3)
        return
    await bot.process_commands(msg)


# ==========================================================
# /ask command (private replies)
# ==========================================================
@tree.command(name="ask", description="Ask TradeHub AI")
async def ask(interaction: discord.Interaction, *, question: str):

    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"⚠️ Use this in <#{ASK_CHANNEL}> only.",
            ephemeral=True)

    q = question.lower()

    # middleman ticket
    if any(x in q for x in ["middleman", "need mm", "mm ticket", "call mm"]):
        cat = interaction.guild.get_channel(CHANNELS["mm_cat"])
        ch = await cat.create_text_channel(f"mm-{interaction.user.name}")
        return await interaction.response.send_message(
            f"🎫 Middleman ticket created: {ch.mention}", ephemeral=True)

    # support ticket
    if any(x in q for x in ["scam", "help", "support", "ticket"]):
        cat = interaction.guild.get_channel(CHANNELS["support_cat"])
        ch = await cat.create_text_channel(f"support-{interaction.user.name}")
        return await interaction.response.send_message(
            f"🟩 Support ticket created: {ch.mention}", ephemeral=True)

    # AI answer
    reply = await phi4(question)
    return await interaction.response.send_message(reply, ephemeral=True)


# ==========================================================
# ready event
# ==========================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI is ONLINE")


# ==========================================================
# RUN BOT
# ==========================================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
