# bot.py
import os
import discord
import aiohttp
import random
import re
from discord import app_commands
from keepalive import keep_alive

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = "microsoft/phi-4"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

ASK_CHANNEL = 1454499949550239955

WELCOME_CHANNEL = 1439885573799284798
RULES_CHANNEL = 1439885040090615930
GIVEAWAYS_CHANNEL = 1445035901561339925
GAMES_CHANNEL = 1451911322563252379
ANNOUNCEMENTS_CHANNEL = 1452292132349022271
AREWELEGIT_CHANNEL = 1452839052738039919
YES_CHANNEL = 1452840180888109067
NO_CHANNEL = 1452840053125546194
TRADING_MAIN = 1439885826292056104
TRADING_MEDIA = 1451977865955639500
SUPPORT_INFO = 1438900168006045907
MM_INFO = 1438899017525362858
MM_REQUEST = 1438899065952927917
VOUCH_FORMAT = 1439598483295309975
VOUCHES_CHANNEL = 1439598519471308861

ROLE_IDS = {
    "owner":               1438892578580730027,
    "co-owner":            1438894594254311504,
    "administrator":       1438895119360065666,
    "head coordinator":    1444915199529324624,
    "coordinator":         1444914892309139529,
    "head moderator":      1441060547700457584,
    "moderator":           1438895276419977329,
    "head manager":        1438895696936828928,
    "manager":             1438895819125297274,
    "head middleman":      1438895916596592650,
    "middleman":           1438896022590984295,
    "member":              1439203750664470589
}

SUPPORT_REPLIES = [
    f"Open a support ticket here: <#{SUPPORT_INFO}> 🎫",
    f"If you think you got scammed or have doubts, go here → <#{SUPPORT_INFO}> 🛠️",
    f"For scam concerns or confusion, ticket here: <#{SUPPORT_INFO}> 🔐",
]

SCAM_ACCUSATION_REPLIES = [
    f"This is not a hitter/scam server. Proof is public in <#{VOUCHES_CHANNEL}> & <#{YES_CHANNEL}> 🛡️",
    f"Check proof before assuming: <#{VOUCHES_CHANNEL}> & <#{YES_CHANNEL}> 🔍",
    f"Everything is legit here, proof channels → <#{VOUCHES_CHANNEL}> + <#{YES_CHANNEL}> 📌",
]

VOUCH_REPLIES = [
    f"All vouches are here: <#{VOUCHES_CHANNEL}> 📦",
    f"You can check proofs here: <#{VOUCHES_CHANNEL}> 🧾",
    f"Trader history is public in: <#{VOUCHES_CHANNEL}> 📁",
]

TRADE_REPLIES = [
    f"You can trade here: <#{TRADING_MAIN}> or <#{TRADING_MEDIA}> ⚖️",
    f"Use these channels to start a deal: <#{TRADING_MAIN}> & <#{TRADING_MEDIA}> 🤝",
    f"Trading channels: <#{TRADING_MAIN}> and <#{TRADING_MEDIA}> 📈",
]

TRADEHUB_SYSTEM_PROMPT = """
You are TradeHub AI. Short, chill, professional replies.
1-3 sentences, 1-2 emojis max.
Do not invent channels or roles.
Owner: Anshuman (<@862948496440819772>)
"""


class TradeHubBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.tree.sync()
        print("🤖 TRADEHUB AI ONLINE")

    async def on_message(self, msg):
        if msg.author.bot: return
        if msg.channel.id == ASK_CHANNEL and not msg.content.startswith("/ask"):
            try: await msg.delete()
            except: pass

bot = TradeHubBot()

@bot.tree.command(name="ask", description="Ask TradeHub AI")
async def ask(interaction: discord.Interaction, question: str):
    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"Use /ask in <#{ASK_CHANNEL}> only. 🚫", ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)
    q = question.lower()

    if "support" in q or "scam" in q or "i got scammed" in q or "doubt" in q:
        return await interaction.followup.send(random.choice(SUPPORT_REPLIES), ephemeral=True)

    if "hitter" in q or "scam server" in q or "fake" in q:
        return await interaction.followup.send(random.choice(SCAM_ACCUSATION_REPLIES), ephemeral=True)

    if "vouch" in q or "vouches" in q or "proof" in q:
        return await interaction.followup.send(random.choice(VOUCH_REPLIES), ephemeral=True)

    if "trade" in q or "deal" in q or "buy" in q or "sell" in q:
        return await interaction.followup.send(random.choice(TRADE_REPLIES), ephemeral=True)

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    body = {"model": OPENROUTER_MODEL,"messages":[{"role":"system","content":TRADEHUB_SYSTEM_PROMPT},{"role":"user","content":question}]}

    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(OPENROUTER_URL,headers=headers,json=body) as r:
                data = await r.json()
        return await interaction.followup.send(data["choices"][0]["message"]["content"], ephemeral=True)
    except:
        return await interaction.followup.send("⚠️ API error, check .env keys.", ephemeral=True)

keep_alive()
bot.run(DISCORD_BOT_TOKEN)
