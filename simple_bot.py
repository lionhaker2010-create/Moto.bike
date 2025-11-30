import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import asyncio
from datetime import datetime

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database import
from database import db

async def start(update, context):
    """Start komandasi - labbey deb javob beradi"""
    user = update.effective_user
    await update.message.reply_text("labbey")
    
    # Foydalanuvchini ma'lumotlar bazasiga qo'shamiz
    db.add_user(user.id, user.first_name)
    
    # Agar admin bo'lsa
    admin_id = os.getenv('ADMIN_ID')
    if admin_id and str(user.id) == str(admin_id):
        from admin import get_admin_keyboard
        await update.message.reply_text(
            "👨‍💼 **Admin Panelga Xush Kelibsiz!**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # Oddiy foydalanuvchi uchun asosiy menyu
    keyboard = ReplyKeyboardMarkup([
        ["🏍️ MotoBike", "🛵 Scooter", "⚡ Electric Scooter Arenda"],
        ["📞 Qo'llab-quvvatlash", "🌐 Tilni o'zgartirish"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "🏠 **Asosiy menyu:**",
        reply_markup=keyboard
    )

async def handle_message(update, context):
    """Oddiy xabarlarni qayta ishlash"""
    text = update.message.text
    
    if "Qo'llab-quvvatlash" in text:
        await update.message.reply_text(
            "📞 **Qo'llab-quvvatlash:** @Operator_Kino_1985\n"
            "☎️ **Telefon:** +998(98)8882505\n\n"
            "🕒 **Ish vaqti:** 09:00 - 18:00"
        )
    elif "Tilni o'zgartirish" in text:
        keyboard = ReplyKeyboardMarkup([
            ["🇺🇿 O'zbek", "🇷🇺 Русский", "🇺🇸 English"]
        ], resize_keyboard=True)
        await update.message.reply_text("🌐 **Tilni tanlang:**", reply_markup=keyboard)
    else:
        await update.message.reply_text("ℹ️ Bu bo'lim tez orada ishga tushadi!")

def main():
    """Asosiy bot funksiyasi"""
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi!")
        return
    
    try:
        # Bot ilovasini yaratish
        application = Application.builder().token(TOKEN).build()
        
        # Handlerlarni qo'shamiz
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", start))  # /admin ham /start kabi
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("🤖 Bot ishga tushdi!")
        
        # Botni ishga tushirish
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Botda xatolik: {e}")
        # Qayta urinish
        import time
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()