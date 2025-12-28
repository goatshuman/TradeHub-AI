import discord, os, random, datetime
from discord.ext import commands
from discord import app_commands
from keepalive import keep_alive  # required for Render Web Service

# =====================================================================
# CONFIG
# =====================================================================
ASK_CHANNEL = 1454499949550239955

MIDDLEMAN_CATEGORY_ID = 1438898941063205034
SUPPORT_CATEGORY_ID = 1438899881719631983

ROLES = {
    "owner": 1438892578580730027,
    "coowner": 1438894594254311504,
    "admin": 1438895119360065666,
    "headcoord": 1444915199529324624,
    "coord": 1444914892309139529,
    "headmod": 1441060547700457584,
    "mod": 1438895276419977329,
    "headmanager": 1438895696936828928,
    "manager": 1438895819125297274,
    "headmm": 1438895916596592650,
    "middleman": 1438896022590984295,
    "verified": 1439203352406921377,
    "member": 1439203750664470589
}

CH = {
    "welcome": 1439885573799284798,
    "rules": 1439885040090615930,
    "giveaways": 1445035901561339925,
    "games": 1451911322563252379,
    "announcements": 1452292132349022271,
    "are_legit": 1452839052738039919,
    "proof_yes": 1452840180888109067,
    "proof_no": 1452840053125546194,
    "trading": 1439885826292056104,
    "media_trading": 1451977865955639500,
    "support_info": 1438900168006045907,
    "middleman_info": 1438899017525362858,
    "request_middleman": 1438899065952927917,
    "vouch_format": 1439598483295309975,
    "mm_vouches": 1439598519471308861
}

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

# =====================================================================
# SCRIPTED RESPONSES
# =====================================================================
unknown = "I cannot answer that. Ask about TradeHub only. 💬"

trade_msgs = [
    f"Trade here: <#{CH['trading']}> and media trades: <#{CH['media_trading']}> 🤝",
    f"Deals happen in <#{CH['trading']}> and <#{CH['media_trading']}> 🤝"
]

scamproof = [
    f"Proof is public here: <#{CH['mm_vouches']}> and <#{CH['proof_yes']}> 🛡️",
]

# =====================================================================
# DELETE ANY CHAT IN ASK CHANNEL (ONLY /ask ALLOWED)
# =====================================================================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.channel.id == ASK_CHANNEL and not message.content.startswith("/ask"):
        await message.delete()
        await message.channel.send(f"Use /ask here only <#{ASK_CHANNEL}> 💬")
        return
    
    text = message.content.lower()

    # =================== CREATE MIDDLEMAN TICKET ===================
    if any(x in text for x in ["middleman ticket","mm ticket","open mm","create mm"]):
        guild = message.guild
        category = guild.get_channel(MIDDLEMAN_CATEGORY_ID)
        username = message.author.name.lower().replace(" ","-")
        num = random.randint(1000,9999)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            message.author: discord.PermissionOverwrite(view_channel=True)
        }
        for role_id in ROLES.values():
            role = guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)

        ch = await category.create_text_channel(f"mm-{username}-{num}", overwrites=overwrites)
        await message.reply(f"🎫 Middleman ticket created: {ch.mention}")
        return

    # =================== CREATE SUPPORT TICKET ===================
    if any(x in text for x in ["support ticket","need support","open support","help ticket"]):
        guild = message.guild
        category = guild.get_channel(SUPPORT_CATEGORY_ID)
        username = message.author.name.lower().replace(" ","-")
        num = random.randint(1000,9999)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            message.author: discord.PermissionOverwrite(view_channel=True)
        }
        for role_id in ROLES.values():
            role = guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)

        ch = await category.create_text_channel(f"support-{username}-{num}", overwrites=overwrites)
        await message.reply(f"🟩 Support ticket created: {ch.mention}")
        return

    await bot.process_commands(message)

# =====================================================================
# /ASK (MAIN COMMAND)
# =====================================================================
@tree.command(name="ask", description="Ask TradeHub AI (Scripted Only)")
async def ask(interaction: discord.Interaction, *, question: str):
    q = question.lower()
    user = interaction.user

    if interaction.channel.id != ASK_CHANNEL:
        return await interaction.response.send_message(
            f"Use /ask in <#{ASK_CHANNEL}> only 💬", ephemeral=True
        )

    # Time system (user timezone)
    if any(x in q for x in ["time","day","date"]):
        now = datetime.datetime.now()
        return await interaction.response.send_message(
            f"{now.strftime('%I:%M %p')} • {now.strftime('%A')} • {now.strftime('%d/%m/%Y')} ⏰"
        )

    # User role list
    if "what roles do i have" in q:
        user_roles = [r.mention for r in user.roles if r.name != "@everyone"]
        return await interaction.response.send_message(f"Your roles: {', '.join(user_roles)} 👍")

    # Who has role
    for name, rid in ROLES.items():
        if name.replace("_"," ") in q:
            role = interaction.guild.get_role(rid)
            members = ", ".join(m.mention for m in role.members) or "Nobody has this role"
            return await interaction.response.send_message(f"{role.name}: {members} 👍")

    # Vouches
    if "vouch" in q:
        return await interaction.response.send_message(f"Middleman vouches: <#{CH['mm_vouches']}> 🧾")

    # Scam check
    if any(x in q for x in ["scam","fake","legit"]):
        return await interaction.response.send_message(random.choice(scamproof))

    # Trading (Option A)
    if "trade" in q:
        return await interaction.response.send_message(random.choice(trade_msgs))

    # VERIFY & GIVE_VERIFIED LOGIC
    member = ROLES["member"] in [r.id for r in user.roles]
    verified_plus = any(r.id in [ROLES["verified"], ROLES["middleman"]] for r in user.roles)

    if "/verify" in q:
        if member:
            return await interaction.response.send_message("/verify is old and doesn't give roles 👍")
        if verified_plus:
            return await interaction.response.send_message("/verify sends staff review request 👍")

    if "/give_verified" in q:
        if member:
            return await interaction.response.send_message("/give_verified is used after requirements 👍")
        if verified_plus:
            return await interaction.response.send_message("/give_verified does nothing at your level 👍")

    # List channels
    if "channels" in q:
        all_channels = "\n".join(f"<#{cid}>" for cid in CH.values())
        return await interaction.response.send_message(all_channels + " 👍")

    # Unknown / Out-of-scope
    return await interaction.response.send_message(unknown)

# =====================================================================
# BOOT / STARTUP
# =====================================================================
@bot.event
async def on_ready():
    await tree.sync()
    print("🔥 TradeHub AI ONLINE (WEB SERVICE MODE)")


# REQUIRED FOR WEB SERVICE HOSTING
keep_alive()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
