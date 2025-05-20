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

# Определяем шаги
FIO_IM, FIO_DAT = range(2)
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

    # Генерируем черновик
    doc = Document()
    doc.add_heading('Заявление', 0)
    doc.add_paragraph(f"От {user_data['fio_dat']}")
    doc.add_paragraph(f"ФИО в именительном падеже: {user_data['fio_im']}")
    doc.save("/mnt/data/zayavlenie_ali.docx")

    await update.message.reply_text("Готово! Черновик заявления создан. Скачай его по ссылке: zayavlenie_ali.docx")
    return ConversationHandler.END

app = ApplicationBuilder().token("8160024624:AAFAI0alIhc6XdSc6WSB3LgKztxiDh2rYcE").build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIO_IM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_im)],
        FIO_DAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_dat)],
    },
    fallbacks=[]
)

app.add_handler(conv_handler)
app.run_polling()
