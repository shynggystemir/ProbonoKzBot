import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from docx import Document

# Состояния
FIO_IM, FIO_DAT, IIN, DISTRICT = range(4)
user_data = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи своё ФИО в именительном падеже:")
    return FIO_IM

async def get_fio_im(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['fio_im'] = update.message.text.strip()
    await update.message.reply_text("Теперь введи своё ФИО в дательном падеже:")
    return FIO_DAT

async def get_fio_dat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['fio_dat'] = update.message.text.strip()
    await update.message.reply_text("Теперь введи свой ИИН:")
    return IIN

async def get_iin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['iin'] = update.message.text.strip()
    await update.message.reply_text("Теперь введи район проживания:")
    return DISTRICT

async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['district'] = update.message.text.strip()

    doc = Document()
    doc.add_heading('Заявление о взыскании алиментов', 0)
    doc.add_paragraph(f"Заявитель: {user_data['fio_im']} (в дательном падеже: {user_data['fio_dat']})")
    doc.add_paragraph(f"ИИН: {user_data['iin']}")
    doc.add_paragraph(f"Район: {user_data['district']}")

    doc.save("zayavlenie_ali_full.docx")

    with open("zayavlenie_ali_full.docx", "rb") as file:
        await update.message.reply_document(file)

    return ConversationHandler.END

app = ApplicationBuilder().token("PASTE_YOUR_BOT_TOKEN_HERE").build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIO_IM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_im)],
        FIO_DAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_dat)],
        IIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_iin)],
        DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
    },
    fallbacks=[]
)

app.add_handler(conv_handler)
app.run_polling()
