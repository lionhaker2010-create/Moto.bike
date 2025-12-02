from flask import Flask, request, jsonify
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
import asyncio

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot application
bot_app = None

# Conversation holatlari
(LANGUAGE, NAME, PHONE, LOCATION, MAIN_MENU, PRODUCT_SELECTED, 
 PAYMENT_CONFIRMATION, WAITING_LOCATION, PAID_SERVICES_MENU, 
 PREMIUM_MENU, PROMOTIONS_MENU) = range(11)

def setup_bot():
    """Botni setup qilish"""
    global bot_app
    
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi!")
        return None
    
    try:
        # Bot application yaratish
        bot_app = Application.builder().token(TOKEN).build()
        
        # Database import
        from database import db
        
        # Handlers qo'shish
        from admin import get_admin_handler
        bot_app.add_handler(get_admin_handler())
        
        # Conversation handler
        from main_handlers import get_conversation_handler
        bot_app.add_handler(get_conversation_handler())
        
        # Callback handler
        from main_handlers import handle_callback_query
        bot_app.add_handler(CallbackQueryHandler(handle_callback_query))
        
        logger.info("✅ Bot setup completed successfully")
        return bot_app
        
    except Exception as e:
        logger.error(f"❌ Bot setup error: {e}")
        return None

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>🏍️ MotoBike Bot</title></head>
    <body style="text-align: center; padding: 50px; font-family: Arial;">
        <h1>🏍️ MotoBike Bot</h1>
        <p style="color: green; font-weight: bold;">✅ Status: Online va Faol</p>
        <p>Webhook rejimida ishlayapti va hech qachon uxlamaydi!</p>
        <p><a href="/ping">🏓 Ping Test</a> | <a href="/health">📊 Health Check</a></p>
        <p><a href="/setwebhook">🔗 Webhook O'rnatish</a></p>
    </body>
    </html>
    """

@app.route('/ping')
def ping():
    return "🏓 pong"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "motobike-bot-webhook"
    })

@app.route('/setwebhook')
def set_webhook():
    """Webhook o'rnatish"""
    try:
        TOKEN = os.getenv('BOT_TOKEN')
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": webhook_url}
        )
        
        return f"✅ Webhook o'rnatildi!<br>URL: {webhook_url}<br>Response: {response.text}"
    except Exception as e:
        return f"❌ Xatolik: {e}"

@app.route(f'/{os.getenv("BOT_TOKEN")}', methods=['POST'])
async def telegram_webhook():
    """Telegram webhook endpoint"""
    if bot_app is None:
        return "Bot not initialized", 500
    
    try:
        # Update ni olish
        json_data = request.get_json()
        update = Update.de_json(json_data, bot_app.bot)
        
        # Update ni qayta ishlash
        await bot_app.process_update(update)
        
        return "OK"
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@app.route('/keepalive')
def keep_alive():
    """Render.com ni uxlatmaslik uchun"""
    return "✅ Keep-alive ping received"

if __name__ == "__main__":
    # Botni setup qilish
    setup_bot()
    
    # Flask server ishga tushishi
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Flask server starting on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)