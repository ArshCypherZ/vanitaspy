import re
from pyrogram import Client, filters
from motor import motor_asyncio
from vanitaspy import User

vanitas_db = db.vanitas

# vars
API_ID = 1331
API_HASH = "dsnsalams"
TOKEN = "3213:fewinedl"
MONGO_DB_URL = "mongodb://localhost:5432/"

# pyrogram client
app = Client("vanitas", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

# mongodb
mongo = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)
db = mongo["vanitas"]

us = User()

# user check
def banned(user):
    chk = us.get_info(user)
    return bool(chk["blacklisted"])

# handlers
HLRS = re.compile("(?i)(on|off|enable|disable)")
OFF = re.compile("(?i)(off|disable)")
ON = re.compile("(?i)(on|enable)")


@app.on_message(filters.command("antispam", prefixes="/!"))
async def vanitas_handler(client, message):
    args = message.text.split(" ", 1)[1]
    chat = message.chat.id
    vanitas = await vanitas_db.find_one({"chat_id": chat})
    
    if not args:
        await message.reply("Use /antispam enable or disable.")
        return
    elif not re.findall(HLRS, args):
        await message.reply("Provide a valid argument. Like enable/disable/on/off")
        return
    
    if not await client.get_chat_member(chat, message.from_user.id).can_restrict_members:
        return
    
    elif re.findall(ON, args):
        if not vanitas:
            await message.reply("Vanitas Antispam System is already enabled")
            return
        await vanitas_db.delete_one({"chat_id": chat})
        await message.reply(f"Enabled Vanitas Antispam System in **{message.chat.title}** by [{message.from_user.first_name}](tg://user?id={message.from_user.id})")
    
    elif re.findall(OFF, args):
        if vanitas:
            await message.reply("Vanitas Antispam System is already disabled")
            return
        await vanitas_db.insert_one({"chat_id": chat})
        await message.reply(f"Disabled Vanitas Antispam System in **{message.chat.title}** by [{message.from_user.first_name}](tg://user?id={message.from_user.id})")


# ban on welcome
@app.on_chat_action()
async def check_user(client, chat_action):
    chat_id = chat_action.chat.id
    not_vanitas = await vanitas_db.find_one({"chat_id": chat_id})
    if not_vanitas:
        return
    
    if chat_action.new_chat_members:
        for member in chat_action.new_chat_members:
            if banned(member.id):
                try:
                    await client.restrict_chat_member(chat_id, member.id, can_send_messages=False)
                    chec = us.get_info(member.id)
                    txt = f"**This user has been blacklisted in Vanitas Antispam System**\n"
                    txt += f"**Reason:** `{chec['reason']}`\n"
                    txt += f"**Enforcer:** `{chec['enforcer']}`\n\n"
                    txt += "Report for unban at @VanitasSupport"
                    await client.send_message(chat_id, txt)
                except Exception as er:
                    await client.send_message(chat_id, str(er))

app.run()
