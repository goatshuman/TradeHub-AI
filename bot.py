import os
import discord, aiohttp, asyncio
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =========================[ BOT TOKENS ]=============================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PHI4_API_KEY = os.getenv("PHI4_API_KEY")

# =========================[ SERVER CONFIG ]===========================
ASK_CHANNEL = 1454499949550239955

CHANNELS = {
    "trade": 1439885826292056104,
    "trade_media": 1451977865955639500,
    "proof_yes": 1452840180888109067,
    "vouches": 1439598519471308861,
    "support_cat": 1438899881719631983,
    "mm_cat": 1438898941063205034
}

SYSTEM_CONTEXT = f"""
You are TradeHub AI. Be confident, helpful, never say 'I cannot answer'.
If trust questions → show proof & vouches.
If scam/support → create support ticket.
If trading help → send trading channels.
"""

# =========================[ BOT SETUP ]==============================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =========================[ AI REQUEST ]==============================
async def call_ai(prompt):
    if not PHI4_API_KEY:
        return fallback(prompt)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {PHI4_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "TradeHub AI"
    }
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=8) as r:
                res = await r.json()
                if "choices" in res:
                    return res["choices"][0]["message"]["content"]
                return fallback(prompt)
    except:
        return fallback(prompt)

# =========================[ FALLBACK BRAIN ]=========================
def fallback(q):
    q = q.lower()

    if any(x in q for x in ["hi","hello","yo","hey"]):
        return "Hey! 👋 How can I help you? Need trading, support or middleman?"

    if "trade" in q:
        return f"Trade here:\n🔁 <#{CHANNELS['trade']}>\n🖼️ <#{CHANNELS['trade_media']}>"

    if "scam" in q or "support" in q:
        return "If you need help or got scammed, say **open a support ticket**. 🛟"

    if "legit" in q or "trust" in q or "fake" in q:
        return f"Proof & vouches:\n✔️ <#{CHANNELS['vouches']}>\n📌 <#{CHANNELS['proof_yes']}>"

    if "middleman" in q:
        return "I can call a middleman for you — just ask to open a ticket. 🤝"

    return "I'm active! Ask about trading, support, proof, or middleman. 😊"


# =========================[ AUTO DELETE ]============================
@bot.event
async def on_message(msg):
    if msg.author.bot: return
    if msg.channel.id == ASK_CHANNEL and not msg.content.startswith("/ask"):
        await msg.delete()
        return await msg.channel.send("⚠️ Only `/ask` works here.", delete_after=2)
    await bot.process_commands(msg)

# =========================[ /ASK COMMAND ]===========================
@tree.command(name="ask", description="Ask TradeHub AI anything")
async def ask(interaction: discord.Interaction, *, question: str):

    # 📌 IMMEDIATE ACK TO PREVENT 404 ERROR
    await interaction.response.defer(ephemeral=True)

    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.followup.send(
            f"⚠️ Use `/ask` only in <#{ASK_CHANNEL}>.",
            ephemeral=True
        )

    q = question.lower()

    # 🎫 Middleman ticket
    if "middleman" in q or "mm" in q:
        cat = interaction.guild.get_channel(CHANNELS["mm_cat"])
        ch = await cat.create_text_channel(f"mm-{interaction.user.name}")
        return await interaction.followup.send(
            f"🎫 Middleman ticket created: {ch.mention}", ephemeral=True)

    # 🟩 Support ticket
    if any(x in q for x in ["scam","help","ticket","support"]):
        cat = interaction.guild.get_channel(CHANNELS["support_cat"])
        ch = await cat.create_text_channel(f"support-{interaction.user.name}")
        return await interaction.followup.send(
            f"🟩 Support ticket created: {ch.mention}", ephemeral=True)

    # 🧠 AI or fallback
    reply = await call_ai(question)
    await interaction.followup.send(reply, ephemeral=True)

# =========================[ READY ]==================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 BOT ONLINE & RESPONDING FAST (No 404, No crash)")

# =========================[ RUN ]====================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
