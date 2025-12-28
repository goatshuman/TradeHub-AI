import os
import discord, random, datetime
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =====================================================================
# 🔑 TOKEN PLACEHOLDERS (SET IN RENDER OR .env)
# =====================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # leave empty here
PHI4_API_KEY = os.getenv("PHI4_API_KEY")            # leave empty here

if not DISCORD_BOT_TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN missing! Add it in Render environment.")
if not PHI4_API_KEY:
    print("⚠️ PHI4_API_KEY not added (not required for scripted mode).")

# =====================================================================
# CONFIG
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
    "welcome": 1439885573799284798,
    "rules": 1439885040090615930,
    "giveaways": 1445035901561339925,
    "games": 1451911322563252379,
    "announcements": 1452292132349022271,
    "are we legit": 1452839052738039919,
    "proof yes": 1452840180888109067,
    "proof no": 1452840053125546194,
    "trading": 1439885826292056104,
    "media trading": 1451977865955639500,
    "support info": 1438900168006045907,
    "middleman info": 1438899017525362858,
    "request a middleman": 1438899065952927917,
    "vouch format": 1439598483295309975,
    "middleman vouches": 1439598519471308861
}

# =====================================================================
# BOT INITIALIZATION
# =====================================================================
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

# =====================================================================
# DELETE NORMAL MESSAGES + TICKET CREATION
# =====================================================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    text = message.content.lower()

    # Only /ask allowed in the ASK channel
    if message.channel.id == ASK_CHANNEL and not text.startswith("/ask"):
        await message.delete()
        await message.channel.send("⚠️ Use `/ask` here only.", delete_after=3)
        return

    # Middleman ticket creation
    if any(t in text for t in ["middleman ticket","i need a middleman","open mm","mm ticket","create mm"]):
        guild = message.guild
        category = guild.get_channel(MIDDLEMAN_CATEGORY_ID)
        username = message.author.name.replace(" ", "-").lower()
        num = random.randint(1000,9999)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            message.author: discord.PermissionOverwrite(view_channel=True)
        }
        ch = await category.create_text_channel(f"mm-{username}-{num}", overwrites=overwrites)
        return await message.reply(f"🎫 Middleman ticket created: {ch.mention}")

    # Support ticket creation
    if any(t in text for t in ["support ticket","help ticket","open support","i need support","support pls"]):
        guild = message.guild
        category = guild.get_channel(SUPPORT_CATEGORY_ID)
        username = message.author.name.replace(" ", "-").lower()
        num = random.randint(1000,9999)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            message.author: discord.PermissionOverwrite(view_channel=True)
        }
        ch = await category.create_text_channel(f"support-{username}-{num}", overwrites=overwrites)
        return await message.reply(f"🟩 Support ticket created: {ch.mention}")

    await bot.process_commands(message)

# =====================================================================
# /ASK COMMAND (SCRIPTED ANSWERS + ROLE CHECKING)
# =====================================================================
@tree.command(name="ask", description="Ask TradeHub AI (Scripted Only)")
async def ask(interaction: discord.Interaction, *, question: str):
    q = question.lower()
    user = interaction.user

    # Only allowed in ASK channel
    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(f"⚠️ Use `/ask` in <#{ASK_CHANNEL}> only.", ephemeral=True)

    # Greetings
    if q in ["hi","hello","hey","yo","sup","hola"]:
        return await interaction.response.send_message(random.choice(["Hey 👋","Hello 😊","Yo ⚡","Hi there 💬"]), ephemeral=True)

    # User roles
    if "what roles" in q or "my roles" in q:
        roles = [r.mention for r in user.roles if r.name != "@everyone"]
        return await interaction.response.send_message(f"Your roles: {', '.join(roles)}", ephemeral=True)

    # =====================
    # VERIFY LOGIC FIRST
    # =====================
    member = interaction.guild.get_role(ROLES["member only"]) in user.roles
    verified = interaction.guild.get_role(ROLES["verified trader"]) in user.roles
    middleman = interaction.guild.get_role(ROLES["middleman"]) in user.roles

    if "/verify" in q:
        if member:
            return await interaction.response.send_message("🔐 `/verify` is old and does not give roles anymore.", ephemeral=True)
        if verified or middleman:
            return await interaction.response.send_message("📩 `/verify` sends a verification request to staff.", ephemeral=True)

    if "/give_verified" in q:
        if member:
            return await interaction.response.send_message("⭐ `/give_verified` is the working command used to give verified trader role AFTER requirements are met.", ephemeral=True)
        if verified or middleman:
            return await interaction.response.send_message("⚙️ `/give_verified` does nothing for your current role level.", ephemeral=True)

    # =====================
    # ROLE LOOKUP (AFTER VERIFY CHECK)
    # =====================
    for name, role_id in ROLES.items():
        if name in q and not q.startswith("/verify") and not q.startswith("/give_verified"):
            role = interaction.guild.get_role(role_id)
            members = [m.mention for m in role.members]
            if not members:
                return await interaction.response.send_message(f"Nobody currently has the **{role.name}** role.", ephemeral=True)
            return await interaction.response.send_message(f"**{role.name} Members:**\n" + "\n".join(members), ephemeral=True)

    # Trading
    if "trade" in q:
        return await interaction.response.send_message(f"🤝 Trade here: <#{CH['trading']}> or <#{CH['media trading']}>", ephemeral=True)

    # Vouches & scam checks
    if any(x in q for x in ["scam","fake","trust","legit","vouch"]):
        return await interaction.response.send_message(f"🛡 Proof & Vouches: <#{CH['middleman vouches']}>", ephemeral=True)

    # Time
    if "time" in q or "date" in q or "day" in q:
        now = datetime.datetime.now()
        return await interaction.response.send_message(f"⏰ {now.strftime('%I:%M %p')} | {now.strftime('%A')} | {now.strftime('%d/%m/%Y')}", ephemeral=True)

    # Unknown
    return await interaction.response.send_message("I cannot answer that. Ask about TradeHub only. 💬", ephemeral=True)

# =====================================================================
# BOT READY
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI ONLINE — Fully Scripted and Token-Ready")

# =====================================================================
# START BOT
# =====================================================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
