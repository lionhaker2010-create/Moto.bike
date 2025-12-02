import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

logger = logging.getLogger(__name__)

# ... barcha handler funksiyalaringiz bu yerda ...

def get_conversation_handler():
    """Conversation handler yaratish"""
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), get_phone)],
            LOCATION: [MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), get_location)],
            MAIN_MENU: [
                MessageHandler(filters.Regex("^(🏍️ MotoBike|🛵 Scooter|⚡ Electric Scooter Arenda|💼 Pullik Hizmatlar|⭐ Premium|🎁 Aksiya)$"), main_menu),
                # ... qolgan handlerlar ...
            ],
        },
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )