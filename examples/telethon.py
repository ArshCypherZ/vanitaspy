import re

from telethon import events, TelegramClient
from telethon.tl.functions.channels import GetParticipantRequest
from motor import motor_asyncio
from vanitaspy import User

# vars
API_HASH = "ijdsolqa"
API_ID = 12331
TOKEN = "12192121:DQSSA"
MONGO_DB_URL = "mongodb://localhost:5432/"

# connecting to mongodb
mongo = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)
db = mongo["vanitas"]
vanitas_db = db.vanitas

# telethon client
telethn = TelegramClient("telethn", API_ID, API_HASH).start(bot_token=TOKEN)

us = User()
# user check
def banned(user):
    chk = us.get_info(user)
    if chk["blacklisted"]:
        return True
    if not chk["blacklisted"]:
        return False

# handlers
HLRS = re.compile("(?i)(on|off|enable|disable)")
OFF = re.compile("(?i)(off|disable)")
ON = re.compile("(?i)(on|enable)")

# permission check
async def can_ban_users(event, user_id):
    try:
        p = await telethn(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if (isinstance(p.participant, types.ChannelParticipantCreator)):
        return True
    if isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.ban_users:
            await event.reply("You need to be an admin with ban rights!")
            return False
        return True
    await event.reply("Be an admin first.")
    return False

@telethn.on(events.NewMessage(pattern="^[/!](?i)antispam ?(.*)"))
async def vanitas_handerl(van):
    args = van.pattern_match.group(1)
    chat = van.chat_id
    vanitas = await vanitas_db.find_one({"chat_id": chat})
    if not args:
        return await van.reply("Use /antispam enable or disable.")
    elif not re.findall(HLRS, args):
        return await van.reply("Provide a valid argument. Like enable/disable/on/off")
    if not await can_ban_users(van, van.sender_id):
        return
    elif re.findall(ON, args):
        if not vanitas:
            return await van.reply("Vanitas Antispam System is already enabled")
        await vanitas_db.delete_one({"chat_id": chat})
        await van.reply(f"Enabled Vanitas Antispam System in **{van.chat.title}** by [{van.sender.first_name}]({van.sender_id})") 
    elif re.findall(OFF, args):
        if vanitas:
            return await van.reply("Vanitas Antispam System is already disabled")
        await vanitas_db.insert_one({"chat_id": chat})
        await van.reply(f"Disabled Vanitas Antispam System in **{van.chat.title}** by [{van.sender.first_name}]({van.sender_id})")
     
     
# ban on welcome
@telethn.on(events.ChatAction)
async def chk_(event):
    chat_id = event.chat_id
    not_vanitas = await vanitas_db.find_one({"chat_id": chat_id})
    if not_vanitas:
        return
    if event.user_joined or event.user_added:
        if banned(event.user_id):
            try:
                await telethn.edit_permissions(event.chat_id, event.user_id, view_messages=False)
                chec = us.get_info(event.user_id)
                txt = f"**This user has been blacklisted in Vanitas Antispam System**\n"
                txt += f"**Reason:** `{chec['reason']}`\n"
                txt += f"**Enforcer:** `{chec['enforcer']}`\n\n"
                txt += "Report for unban at @VanitasSupport"
                await event.reply(txt, link_preview=False)
            except Exception as er:
                await event.reply(er)
