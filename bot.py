import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from docx import Document

FIO_IM, FIO_DAT, IIN, ADDRESS, PHONE, FIO_IM_DEBTOR, FIO_ROD_DEBTOR, IIN_DEBTOR, ADDRESS_DEBTOR, CHILD_NAME, CHILD_BIRTH, BIRTH_CONFIRMED, MARRIAGE_STATUS, DISTRICT = range(14)
user_data = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи своё ФИО в именительном падеже:")
    return FIO_IM

async def get_input(update: Update, context: ContextTypes.DEFAULT_TYPE, key, next_state):
    user_data[key] = update.message.text
    return next_state

async def get_fio_im(update, context): return await get_input(update, context, 'fio_im', FIO_DAT)
async def get_fio_dat(update, context): return await get_input(update, context, 'fio_dat', IIN)
async def get_iin(update, context): return await get_input(update, context, 'iin', ADDRESS)
async def get_address(update, context): return await get_input(update, context, 'address', PHONE)
async def get_phone(update, context): return await get_input(update, context, 'phone', FIO_IM_DEBTOR)
async def get_fio_im_debtor(update, context): return await get_input(update, context, 'fio_im_debtor', FIO_ROD_DEBTOR)
async def get_fio_rod_debtor(update, context): return await get_input(update, context, 'fio_rod_debtor', IIN_DEBTOR)
async def get_iin_debtor(update, context): return await get_input(update, context, 'iin_debtor', ADDRESS_DEBTOR)
async def get_address_debtor(update, context): return await get_input(update, context, 'address_debtor', CHILD_NAME)
async def get_child_name(update, context): return await get_input(update, context, 'child_name', CHILD_BIRTH)
async def get_child_birth(update, context): return await get_input(update, context, 'child_birth', BIRTH_CONFIRMED)

async def get_birth_confirmed(update, context):
    if update.message.text.lower() != "да":
        await update.message.reply_text("Если должник не указан в свидетельстве — подаётся иск, а не судебный приказ.")
        return ConversationHandler.END
    return MARRIAGE_STATUS

async def get_marriage_status(update, context): return await get_input(update, context, 'marriage_status', DISTRICT)

async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['district'] = update.message.text
    generate_document()
    await update.message.reply_text("Черновик заявления создан. Скачай его по ссылке: zayavlenie_ali.docx")
    return ConversationHandler.END

def generate_document():
    doc = Document()
    doc.add_heading('Заявление', 0)
    doc.add_paragraph(f"От {user_data['fio_dat']} (ИИН: {user_data['iin']})")
    doc.add_paragraph(f"Адрес: {user_data['address']}")
    doc.add_paragraph(f"Телефон: {user_data['phone']}")
    doc.add_paragraph("... (тело заявления вставляется по шаблону) ...")
    doc.save("/mnt/data/zayavlenie_ali.docx")

app = ApplicationBuilder().token("8160024624:AAFAI0alIhc6XdSc6WSB3LgKztxiDh2rYcE").build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIO_IM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_im)],
        FIO_DAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_dat)],
        IIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_iin)],
        ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        FIO_IM_DEBTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_im_debtor)],
        FIO_ROD_DEBTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio_rod_debtor)],
        IIN_DEBTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_iin_debtor)],
        ADDRESS_DEBTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address_debtor)],
        CHILD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_child_name)],
        CHILD_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_child_birth)],
        BIRTH_CONFIRMED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birth_confirmed)],
        MARRIAGE_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_marriage_status)],
        DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
    },
    fallbacks=[]
)

app.add_handler(conv_handler)
app.run_polling()
