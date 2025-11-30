import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
import sqlite3

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleDB:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Oddiy ma'lumotlar bazasi"""
        try:
            conn = sqlite3.connect('simple_bot.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    registered BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("✅ Simple database created")
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    def add_user(self, user_id, first_name):
        """Foydalanuvchi qo'shish"""
        try:
            conn = sqlite3.connect('simple_bot.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)',
                (user_id, first_name)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Add user error: {e}")

# Database obyekti
db = SimpleDB()

async def start(update, context):
    """Start komandasi - faqat labbey deb javob beradi"""
    user = update.effective_user
    
    # Foydalanuvchini bazaga qo'shamiz
    db.add_user(user.id, user.first_name)
    
    # LABBEY javobi
    await update.message.reply_text("labbey")
    
    # Asosiy menyu
    keyboard = ReplyKeyboardMarkup([
        ["🏍️ MotoBike", "🛵 Scooter", "⚡ Electric Scooter"],
        ["📞 Support", "🌐 Change Language"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "🏠 **Main Menu** - Choose an option:",
        reply_markup=keyboard
    )

async def handle_message(update, context):
    """Xabarlarni qayta ishlash"""
    text = update.message.text
    
    if "Support" in text or "Qo'llab-quvvatlash" in text:
        await update.message.reply_text(
            "📞 **Support:** @Operator_Kino_1985\n"
            "☎️ **Phone:** +998(98)8882505\n\n"
            "🕒 **Working hours:** 09:00 - 18:00"
        )
    elif "Change Language" in text or "Tilni o'zgartirish" in text:
        keyboard = ReplyKeyboardMarkup([
            ["🇺🇿 O'zbek", "🇷🇺 Русский", "🇺🇸 English"]
        ], resize_keyboard=True)
        await update.message.reply_text("🌐 **Select language:**", reply_markup=keyboard)
    else:
        await update.message.reply_text("✅ This section will be available soon!")

async def admin_command(update, context):
    """Admin komandasi"""
    user = update.effective_user
    admin_id = os.getenv('ADMIN_ID')
    
    if admin_id and str(user.id) == str(admin_id):
        keyboard = ReplyKeyboardMarkup([
            ["📦 Add Product", "🗑️ Delete Product"],
            ["👥 Users", "📊 Statistics"],
            ["🔙 Main Menu"]
        ], resize_keyboard=True)
        
        await update.message.reply_text(
            "👨‍💼 **Admin Panel**\n\nSelect an option:",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text("❌ You are not admin!")

def main():
    """Asosiy bot funksiyasi"""
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("❌ BOT_TOKEN not found!")
        return
    
    try:
        # Bot ilovasini yaratish
        application = Application.builder().token(TOKEN).build()
        
        # Handlerlarni qo'shamiz
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("🤖 Bot started successfully!")
        print("🚀 Bot is running...")
        
        # Botni ishga tushirish
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        print(f"❌ Error: {e}")
        # Qayta urinish
        import time
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()