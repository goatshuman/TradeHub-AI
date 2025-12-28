import discord
from discord import app_commands
from discord.ext import commands
import random
import aiohttp
from datetime import datetime

# =====================================================
# 🔑 FILL THESE YOURSELF
# =====================================================
TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
PHI4_API_KEY = ""  # <--- leave blank & fill by yourself

SERVER_NAME = "TradeHub"

# =====================================================
# 📌 CHANNEL IDS
# =====================================================
PROOF_YES = 1452840180888109067
PROOF_POLL = 1452839052738039919
REQ_MM = 1438899065952927917
MM_VOUCHES = 1439598519471308861

# TICKET CATEGORIES
MM_TICKET_CATEGORY = 1438898941063205034
SUPPORT_TICKET_CATEGORY = 1438899881719631983

# =====================================================
# 🎭 ROLE IDS
# =====================================================
OWNER = 1438892578580730027
COOWNER = 1438894594254311504
ADMIN = 1438895119360065666
HEAD_CORD = 1444915199529324624
CORD = 1444914892309139529
HEAD_MOD = 1441060547700457584
MOD = 1438895276419977329
HEAD_MANAGER = 1438895696936828928
MANAGER = 1438895819125297274
HEAD_MM = 1438895916596592650
MIDDLEMAN = 1438896022590984295
VERIFIED = 1439203352406921377
MEMBER = 1439203750664470589

# =====================================================
# 🧠 OPTIONAL PHI-4 (Controlled)
# =====================================================
async def phi4_scripted(question: str):
    if PHI4_API_KEY == "":
        return "❌ No Phi-4 key set. Please fill PHI4_API_KEY."

    script = """
    You are a scripted bot for a trading server.
    Do not invent information. Do not guess.
    Never guarantee trades. Always recommend a middleman.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model":"phi-4",
                "messages":[
                    {"role":"system","content":script},
                    {"role":"user","content":question}
                ]
            },
            headers={"Authorization":f"Bearer {PHI4_API_KEY}"}
        ) as r:
            data = await r.json()
            return data["choices"][0]["message"]["content"]

# =====================================================
# 🤖 BOT SETUP
# =====================================================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =====================================================
# ROTATING REPLIES
# =====================================================
LEGIT_RESPONSES = [
    f"✔️ This server is legit based on vouches & successful trades. Proof: <#{MM_VOUCHES}>",
    f"🛡️ Yes, this server is considered legit. Always trade with a middleman.",
    f"📌 Verified proof & trades shown in <#{MM_VOUCHES}> <#{PROOF_YES}>",
    f"✨ We are legit based on history & proof. Trade safely with MM."
]

PROOF_RESPONSES = [
    f"📌 Proof: <#{MM_VOUCHES}> <#{PROOF_YES}>",
    f"✔️ View vouches here: <#{MM_VOUCHES}>",
    f"🛡️ MM + vouches = safety. Proof: <#{MM_VOUCHES}>",
    f"📍 Confirmations: <#{MM_VOUCHES}> <#{PROOF_YES}>"
]

# =====================================================
# ROLE CHECK
# =====================================================
def has_role(user, role_id):
    return any(r.id == role_id for r in user.roles)

def role_list(member):
    return [r.name for r in member.roles if r.name != "@everyone"]

# =====================================================
# 🎯 /ask COMMAND
# =====================================================
@tree.command(name="ask", description="Ask the TradeHub bot something.")
async def ask(interaction: discord.Interaction, question: str):
    q = question.lower()
    guild = interaction.guild

    # ---- LEGIT CHECK ----
    if any(x in q for x in ["legit", "real", "trusted"]):
        return await interaction.response.send_message(random.choice(LEGIT_RESPONSES), ephemeral=True)

    # ---- PROOF CHECK ----
    if "proof" in q or "vouches" in q:
        return await interaction.response.send_message(random.choice(PROOF_RESPONSES), ephemeral=True)

    # ---- TIME ----
    if "time" in q:
        current_time = datetime.now().strftime("%I:%M %p")
        return await interaction.response.send_message(f"⏰ Current time: **{current_time}**", ephemeral=True)

    # ---- DATE ----
    if "date" in q or "today" in q:
        today = datetime.now().strftime("%d-%m-%Y")
        return await interaction.response.send_message(f"📅 Today’s date: **{today}**", ephemeral=True)

    # ---- MY ROLES ----
    if "my roles" in q:
        return await interaction.response.send_message(
            f"🎭 Your roles: {', '.join(role_list(interaction.user))}", ephemeral=True)

    # ---- OTHER USER ROLES ----
    if "roles of" in q or "what is @" in q:
        target = None
        for user in interaction.guild.members:
            if user.mention in question or user.name.lower() in q:
                target = user
                break
        if target:
            return await interaction.response.send_message(
                f"🎭 {target.display_name}'s roles: {', '.join(role_list(target))}", ephemeral=True)
        return await interaction.response.send_message("❓ Mention a user.", ephemeral=True)

    # ---- WHO IS OWNER / CO-OWNER ----
    if "who is owner" in q or "owner?" in q:
        owners = [m.mention for m in guild.members if has_role(m, OWNER)]
        return await interaction.response.send_message(
            f"👑 Owner: {', '.join(owners)}", ephemeral=True)

    if "co-owner" in q or "co owner" in q:
        co = [m.mention for m in guild.members if has_role(m, COOWNER)]
        return await interaction.response.send_message(
            f"🔱 Co-Owner: {', '.join(co)}", ephemeral=True)

    # ---- WHO ARE MEMBERS ----
    if "who are members" in q:
        return await interaction.response.send_message(
            "👥 There are too many members to mention individually.", ephemeral=True)

    # ---- OPEN MIDDLEMAN TICKET ----
    if "make mm ticket" in q or "open mm" in q:
        category = guild.get_channel(MM_TICKET_CATEGORY)
        ticket = await guild.create_text_channel(f"mm-ticket-{interaction.user.name}", category=category)
        return await interaction.response.send_message(f"🎫 Middleman ticket created: {ticket.mention}", ephemeral=True)

    # ---- OPEN SUPPORT TICKET ----
    if "make support" in q or "open support" in q:
        category = guild.get_channel(SUPPORT_TICKET_CATEGORY)
        ticket = await guild.create_text_channel(f"support-{interaction.user.name}", category=category)
        return await interaction.response.send_message(f"📩 Support ticket created: {ticket.mention}", ephemeral=True)

    # ---- FALLBACK TO PHI-4 ----
    ai = await phi4_scripted(question)
    return await interaction.response.send_message(ai, ephemeral=True)

# =====================================================
# 🚀 START BOT
# =====================================================
@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} is live in {SERVER_NAME}")

bot.run(TOKEN)
