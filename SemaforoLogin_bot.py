import os
import logging
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Configurazione Logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv('TOKEN', '8657478478:AAF3RSiDG5yNV8j9G5IClFXBSTy0of9kyoY')
stato = {"colore": "🟢 VERDE", "utente_id": None, "messaggio_pin_id": None}

# --- PARTE PER KOYEB FREE: Health Check Server ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return # Silenzia i log del server web

def run_health_server():
    # Koyeb usa la porta 8000 o quella definita in PORT
    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logging.info(f"Health check server avviato sulla porta {port}")
    server.serve_forever()
# ------------------------------------------------

async def aggiorna_semaforo(context, chat_id):
    testo = f"🚦 **STATO LOGIN AL DESKTOP REMOTO ** 🚦\n\nAttuale: {stato['colore']}"
    if stato['utente_id']:
        testo += f"\nOccupato da: ID {stato['utente_id']}"
    
    try:
        if stato['messaggio_pin_id'] is None:
            msg = await context.bot.send_message(chat_id=chat_id, text=testo, parse_mode='Markdown')
            stato['messaggio_pin_id'] = msg.message_id
            await context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id)
        else:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=stato['messaggio_pin_id'], text=testo, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Errore Pin: {e}")

async def occupa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if stato['colore'] == "🟢 VERDE":
        stato['colore'] = "🔴 ROSSO"
        stato['utente_id'] = user.id
        await aggiorna_semaforo(context, update.effective_chat.id)
        await update.message.reply_text(f"🔴 Semaforo occupato da {user.first_name}")
    else:
        await update.message.reply_text("❌ Già occupato!")

async def libera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if stato['colore'] == "🔴 ROSSO" and user.id == stato['utente_id']:
        stato['colore'] = "🟢 VERDE"
        stato['utente_id'] = None
        await aggiorna_semaforo(context, update.effective_chat.id)
        await update.message.reply_text("🟢 Semaforo libero!")
    elif stato['colore'] == "🔴 ROSSO":
        await update.message.reply_text("⚠️ Non puoi liberarlo tu!")

if __name__ == '__main__':
    # Avvia il server di salute in un thread separato
    Thread(target=run_health_server, daemon=True).start()
    
    # Avvia il bot Telegram
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("occupa", occupa))
    app.add_handler(CommandHandler("libera", libera))
    
    logging.info("Bot in esecuzione...")
    app.run_polling()
