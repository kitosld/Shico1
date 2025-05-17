import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from pathlib import Path

BOT_TOKEN = "7733092460:AAFDHYW16CxVWMuH7QX04z2QFwzpuAXVHP8"

PACKS_FILE = "banned_packs.json"
GIFS_FILE = "banned_gifs.json"

def load_json(path):
    if Path(path).exists():
        with open(path, "r") as f:
            return set(json.load(f))
    return set()

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(list(data), f)

banned_packs = load_json(PACKS_FILE)
banned_gifs = load_json(GIFS_FILE)

async def banpack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.sticker:
        pack = update.message.reply_to_message.sticker.set_name
        if pack:
            banned_packs.add(pack)
            save_json(PACKS_FILE, banned_packs)
            await update.message.reply_text(f"Стикерпак "{pack}" заблокирован.")
        else:
            await update.message.reply_text("У стикера нет названия пака.")
    else:
        await update.message.reply_text("Ответь на стикер, который хочешь заблокировать.")

async def unbanpack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.sticker:
        pack = update.message.reply_to_message.sticker.set_name
        if pack in banned_packs:
            banned_packs.remove(pack)
            save_json(PACKS_FILE, banned_packs)
            await update.message.reply_text(f"Стикерпак "{pack}" разблокирован.")
        else:
            await update.message.reply_text("Этот пак не был заблокирован.")
    else:
        await update.message.reply_text("Ответь на стикер, который хочешь разблокировать.")

async def listpacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not banned_packs:
        await update.message.reply_text("Нет заблокированных стикерпаков.")
    else:
        msg = "Заблокированные паки:
" + "\n".join(f"• {p}" for p in banned_packs)
        await update.message.reply_text(msg)

async def bangif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.animation:
        file_id = update.message.reply_to_message.animation.file_unique_id
        banned_gifs.add(file_id)
        save_json(GIFS_FILE, banned_gifs)
        await update.message.reply_text("Гифка заблокирована.")
    else:
        await update.message.reply_text("Ответь на гифку, которую хочешь заблокировать.")

async def unbangif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.animation:
        file_id = update.message.reply_to_message.animation.file_unique_id
        if file_id in banned_gifs:
            banned_gifs.remove(file_id)
            save_json(GIFS_FILE, banned_gifs)
            await update.message.reply_text("Гифка разблокирована.")
        else:
            await update.message.reply_text("Эта гифка не была заблокирована.")
    else:
        await update.message.reply_text("Ответь на гифку, которую хочешь разблокировать.")

async def listgifs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not banned_gifs:
        await update.message.reply_text("Нет заблокированных гифок.")
    else:
        msg = "Заблокированные гифки (ID):\n" + "\n".join(banned_gifs)
        await update.message.reply_text(msg)

async def delete_blocked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg.sticker and msg.sticker.set_name in banned_packs:
        await msg.delete()
    elif msg.animation and msg.animation.file_unique_id in banned_gifs:
        await msg.delete()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("banpack", banpack))
    app.add_handler(CommandHandler("unbanpack", unbanpack))
    app.add_handler(CommandHandler("listpacks", listpacks))
    app.add_handler(CommandHandler("bangif", bangif))
    app.add_handler(CommandHandler("unbangif", unbangif))
    app.add_handler(CommandHandler("listgifs", listgifs))
    app.add_handler(MessageHandler(filters.ALL, delete_blocked))

    print("Bot started...")
    app.run_polling()