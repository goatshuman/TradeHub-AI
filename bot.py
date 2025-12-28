import os
import discord, random, datetime
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive

# =====================================================================
# 🔑 TOKEN PLACEHOLDERS (SET IN RENDER / .env)
# =====================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # leave blank here
PHI4_API_KEY = os.getenv("PHI4_API_KEY")            # leave blank here

if not DISCORD_BOT_TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN missing in ENV!")
if not PHI4_API_KEY:
    print("⚠️ PHI4_API_KEY missing (not required for scripted mode)")

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
    "trading": 1439885826292056104,
    "media trading": 1451977865955639500,
    "middleman vouches": 1439598519471308861,
    "proof yes": 1452840180888109067
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# =====================================================================
# AUTO DELETE TEXT IN ASK CHANNEL + SMART TICKET CREATION
# =====================================================================
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    text = msg.content.lower()

    # prevent chatting in ask channel
    if msg.channel.id == ASK_CHANNEL and not text.startswith("/ask"):
        await msg.delete()
        await msg.channel.send("⚠️ Use `/ask` here only.", delete_after=3)
        return

    # MIDDLEMAN TICKET TRIGGERS (PRIORITY #1)
    if any(x in text for x in [
        "middleman ticket","open mm","create mm","need a middleman","call middleman",
        "i need mm","mm ticket","send mm"
    ]):
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

    # SUPPORT TICKET TRIGGERS (PRIORITY #2)
    if any(x in text for x in [
        "support ticket","open support","help ticket","i need support","i got scammed","support me"
    ]):
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
# /ASK MAIN COMMAND
# =====================================================================
@tree.command(name="ask", description="Ask TradeHub AI — Scripted & Safe Replies.")
async def ask(interaction: discord.Interaction, *, question: str):
    q = question.lower()
    user = interaction.user

    # CHANNEL CHECK
    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"⚠️ Use this in <#{ASK_CHANNEL}> only.", ephemeral=True
        )

    # ==================================
    # BASIC GREETINGS
    # ==================================
    if q in ["hi","hello","hey","yo","sup","hola"]:
        return await interaction.response.send_message(
            random.choice(["Hey! 👋","Hello 😊","Yo ⚡","Hi there 💬"]),
            ephemeral=True
        )

    # ==================================
    # VERIFY COMMANDS (PRIORITY)
    # ==================================
    member = interaction.guild.get_role(ROLES["member only"]) in user.roles
    verified = interaction.guild.get_role(ROLES["verified trader"]) in user.roles
    mm = interaction.guild.get_role(ROLES["middleman"]) in user.roles

    if "/verify" in q:
        if member:
            return await interaction.response.send_message(
                "🔐 `/verify` is old and no longer gives roles.",
                ephemeral=True
            )
        return await interaction.response.send_message(
            "📩 `/verify` sends a verification request to staff.",
            ephemeral=True
        )

    if "/give_verified" in q:
        if member:
            return await interaction.response.send_message(
                "⭐ `/give_verified` gives verified role **after real trading requirements only.**",
                ephemeral=True
            )
        return await interaction.response.send_message(
            "⚙️ `/give_verified` does nothing for your current role level.",
            ephemeral=True
        )

    # ==================================
    # ROLE LOOKUP (SMART MATCH)
    # ==================================
    for name, role_id in ROLES.items():
        # prevent "owner" activating inside "co-owner"
        if name == "co-owner" and "co-owner" in q:
            role = interaction.guild.get_role(role_id)
            members = [m.mention for m in role.members]
            return await interaction.response.send_message("\n".join(members), ephemeral=True)

        # normal role lookup
        if name in q and name != "owner":  # no wrong owner confusion
            role = interaction.guild.get_role(role_id)
            members = [m.mention for m in role.members]
            if not members:
                return await interaction.response.send_message(
                    f"No one currently has **{role.name}** ❌",
                    ephemeral=True
                )
            return await interaction.response.send_message(
                f"**{role.name} Members:**\n" + "\n".join(members),
                ephemeral=True
            )

    # ==================================
    # TRADING
    # ==================================
    if "trade" in q or "trading" in q:
        return await interaction.response.send_message(
            f"🤝 Trade here: <#{CH['trading']}> or <#{CH['media trading']}>",
            ephemeral=True
        )

    # ==================================
    # DEFENSIVE / CONFIDENT NEGATIVE RESPONSE
    # ==================================
    if any(x in q for x in ["scam","fake","hit","fraud","cheat","not legit"]):
        replies = [
            f"🛡 **Respectfully:** Proof is public in <#{CH['middleman vouches']}> & <#{CH['proof yes']}>. Please check before assuming.",
            f"📌 **Direct:** Claims don't matter — evidence does. Proof is available in <#{CH['middleman vouches']}>."
        ]
        return await interaction.response.send_message(random.choice(replies), ephemeral=True)

    # ==================================
    # TIME / DATE
    # ==================================
    if any(x in q for x in ["time","date","day"]):
        now = datetime.datetime.now()
        return await interaction.response.send_message(
            f"⏰ {now.strftime('%I:%M %p')} | {now.strftime('%A')} | {now.strftime('%d/%m/%Y')}",
            ephemeral=True
        )

    # ==================================
    # DEFAULT FAIL-SAFE
    # ==================================
    return await interaction.response.send_message(
        "I cannot answer that. Ask something related to TradeHub only. 💬",
        ephemeral=True
    )

# =====================================================================
# BOT READY
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI ONLINE — Defensive + Confident Mode Enabled")

# =====================================================================
# START BOT (RENDER SAFE)
# =====================================================================
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
