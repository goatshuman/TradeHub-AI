import os
import discord, random, datetime
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =====================================================================
# 🔑 TOKENS (SET THESE IN RENDER / .env - DO NOT PUT IN CODE)
# =====================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # leave blank here
PHI4_API_KEY = os.getenv("PHI4_API_KEY")            # optional for future
if not DISCORD_BOT_TOKEN:
    print("❌ DISCORD_BOT_TOKEN missing in environment!")

# =====================================================================
# SERVER CONFIG
# =====================================================================
ASK_CHANNEL = 1454499949550239955

MIDDLEMAN_CATEGORY_ID = 1438898941063205034
SUPPORT_CATEGORY_ID = 1438899881719631983

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

CH = {
    "trading": 1439885826292056104,
    "media trading": 1451977865955639500,
    "middleman vouches": 1439598519471308861,
    "proof yes": 1452840180888109067
}

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

# =====================================================================
# ✋ AUTO DELETE IN ASK CHANNEL & OPEN TICKETS
# =====================================================================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    text = msg.content.lower()

    # Main channel lock
    if msg.channel.id == ASK_CHANNEL and not text.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Use `/ask` here only.", delete_after=3)
        return

    # 🎫 Middleman ticket trigger
    if any(x in text for x in ["middleman ticket","open mm","create mm","need a middleman","mm ticket","call a middleman"]):
        guild = msg.guild
        category = guild.get_channel(MIDDLEMAN_CATEGORY_ID)
        username = msg.author.name.lower().replace(" ","-")
        num = random.randint(1000,9999)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            msg.author: discord.PermissionOverwrite(view_channel=True)
        }
        ch = await category.create_text_channel(f"mm-{username}-{num}", overwrites=overwrites)
        return await msg.reply(f"🎫 Middleman ticket created: {ch.mention}")

    # 🟩 Support ticket trigger
    if any(x in text for x in ["support ticket","i need support","help ticket","open support","got scammed","support me"]):
        guild = msg.guild
        category = guild.get_channel(SUPPORT_CATEGORY_ID)
        username = msg.author.name.lower().replace(" ","-")
        num = random.randint(1000,9999)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            msg.author: discord.PermissionOverwrite(view_channel=True)
        }
        ch = await category.create_text_channel(f"support-{username}-{num}", overwrites=overwrites)
        return await msg.reply(f"🟩 Support ticket created: {ch.mention}")

    await bot.process_commands(msg)

# =====================================================================
# 🤖 SMART BRAIN — UNDERSTANDS MEANING, NOT KEYWORDS ONLY
# =====================================================================
legit_questions = [
    "is this server legit","is this legit","can i trust this server","is trading safe here",
    "is this real","are trades real here","can i trust you","this real or fake"
]

accusations = [
    "this is scam","you scam","server fake","you guys fake","this is hit","hitter server",
    "not legit","fraud","cheat","you will scam","you hit people"
]

# =====================================================================
# /ASK — MAIN LOGIC
# =====================================================================
@tree.command(name="ask", description="Ask TradeHub AI — Smart & Controlled Replies.")
async def ask(interaction: discord.Interaction, *, question: str):
    q = question.lower()
    user = interaction.user

    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(f"⚠️ Use `/ask` in <#{ASK_CHANNEL}> only.", ephemeral=True)

    # --- Greetings ---
    if q in ["hi","hello","hey","yo","sup","hola","hi there"]:
        return await interaction.response.send_message(random.choice([
            "Hey 👋","Hello 😊","Yo ⚡","Hi there 💬"
        ]), ephemeral=True)

    # --- Legit Check / Trust Questions ---
    for phrase in legit_questions:
        if phrase in q:
            return await interaction.response.send_message(random.choice([
                f"🛡 **Respectfully:** Yes — proof of real trades is public in <#{CH['middleman vouches']}> & <#{CH['proof yes']}>.",
                f"📌 **Direct:** Claims don't matter — evidence does. Check <#{CH['middleman vouches']}> for yourself.",
            ]), ephemeral=True)

    # --- Accusations / Negative Claims ---
    for phrase in accusations:
        if phrase in q:
            return await interaction.response.send_message(random.choice([
                f"📌 Evidence speaks louder than accusations. Proof & transparency are public in <#{CH['middleman vouches']}>.",
                f"🛡 Please check real proof before assuming — it's all visible in <#{CH['middleman vouches']}> & <#{CH['proof yes']}>.",
            ]), ephemeral=True)

    # --- Verify / Give Verified ---
    member = interaction.guild.get_role(ROLES["member only"]) in user.roles
    verified = interaction.guild.get_role(ROLES["verified trader"]) in user.roles
    mm = interaction.guild.get_role(ROLES["middleman"]) in user.roles

    if "/verify" in q:
        return await interaction.response.send_message(
            "🔐 `/verify` is old for members & does not give roles. Verified+ ranks use it for reviewer request.", ephemeral=True)

    if "/give_verified" in q:
        if member:
            return await interaction.response.send_message(
                "⭐ `/give_verified` is the working command for verified role *after completing requirements*.", ephemeral=True)
        return await interaction.response.send_message(
            "⚙️ `/give_verified` does nothing for higher ranks — it's normal.", ephemeral=True)

    # --- Role Lookup (with co-owner fix) ---
    for name, role_id in ROLES.items():
        if name == "co-owner" and "co-owner" in q:
            role = interaction.guild.get_role(role_id)
            members = [m.mention for m in role.members]
            return await interaction.response.send_message("\n".join(members), ephemeral=True)

        if name in q and name != "owner":  # avoids owner/co-owner confusion
            role = interaction.guild.get_role(role_id)
            members = [m.mention for m in role.members]
            return await interaction.response.send_message(
                f"**{role.name} Members:**\n" + ("\n".join(members) if members else "None yet"), ephemeral=True)

    # --- Trading ---
    if "trade" in q or "trading" in q:
        return await interaction.response.send_message(
            f"🤝 Trade in <#{CH['trading']}> or <#{CH['media trading']}> with a middleman for safety.", ephemeral=True)

    # --- Time / Date ---
    if any(x in q for x in ["time","date","day"]):
        now = datetime.datetime.now()
        return await interaction.response.send_message(
            f"⏰ {now.strftime('%I:%M %p')} | {now.strftime('%A')} | {now.strftime('%d/%m/%Y')}", ephemeral=True)

    # --- Default Fallback ---
    return await interaction.response.send_message(
        "I cannot answer that. Ask something related to TradeHub only. 💬", ephemeral=True)

# =====================================================================
# BOT READY
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI ONLINE — Smart Brain Enabled (Respectful + Confident Mode)")

# =====================================================================
# START BOT (RENDER SAFE)
# =====================================================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
