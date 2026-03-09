from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8657478478:AAF3RSiDG5yNV8j9G5IClFXBSTy0of9kyoY'

# Variabili di stato
stato = {"colore": "🟢 VERDE", "utente_id": None, "messaggio_pin_id": None}

async def aggiorna_semaforo(context, chat_id):
    testo = f"🚦 **STATO SEMAFORO** 🚦\n\nAttuale: {stato['colore']}"
    if stato['utente_id']:
        testo += f"\nOccupato da: ID {stato['utente_id']}"
    
    # Se è la prima volta, invia e fissa. Altrimenti modifica.
    if stato['messaggio_pin_id'] is None:
        msg = await context.bot.send_message(chat_id=chat_id, text=testo, parse_mode='Markdown')
        stato['messaggio_pin_id'] = msg.message_id
        await context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id)
    else:
        await context.bot.edit_message_text(
            chat_id=chat_id, 
            message_id=stato['messaggio_pin_id'], 
            text=testo, 
            parse_mode='Markdown'
        )

async def occupa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if stato['colore'] == "🟢 VERDE":
        stato['colore'] = "🔴 ROSSO"
        stato['utente_id'] = user.id
        await aggiorna_semaforo(context, update.effective_chat.id)
        await update.message.reply_text(f"Hai occupato il semaforo, {user.first_name}!")
    else:
        await update.message.reply_text("Alt! È già occupato.")

async def libera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if stato['colore'] == "🔴 ROSSO":
        if user.id == stato['utente_id']:
            stato['colore'] = "🟢 VERDE"
            stato['utente_id'] = None
            await aggiorna_semaforo(context, update.effective_chat.id)
            await update.message.reply_text("Semaforo liberato!")
        else:
            await update.message.reply_text("Non puoi liberarlo tu!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("occupa", occupa))
app.add_handler(CommandHandler("libera", libera))
app.run_polling()
