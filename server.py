# server.py
from flask import Flask, jsonify, request
import os
import logging
from telegram import Update
from telegram.ext import Application, ContextTypes
import asyncio

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot application
bot_application = None

def setup_bot():
    """Botni setup qilish"""
    global bot_application
    try:
        from main import create_application
        
        TOKEN = os.getenv('BOT_TOKEN')
        if not TOKEN:
            logger.error("BOT_TOKEN topilmadi!")
            return None
        
        bot_application = create_application(TOKEN)
        logger.info("✅ Bot application created successfully")
        return bot_application
        
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
        <p>Bot webhook rejimida ishlayapti va hech qachon uxlamaydi!</p>
        <p><a href="/ping">🏓 Ping Test</a> | <a href="/health">📊 Health Check</a></p>
        <p><a href="/set_webhook">🔗 Webhook O'rnatish</a> | <a href="/delete_webhook">🗑️ Webhook O'chirish</a></p>
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
        "service": "motobike-bot-webhook",
        "timestamp": time.time(),
        "port": os.environ.get("PORT", 8080)
    })

@app.route('/set_webhook')
def set_webhook():
    """Webhook o'rnatish"""
    try:
        TOKEN = os.getenv('BOT_TOKEN')
        if not TOKEN:
            return "BOT_TOKEN topilmadi!", 500
        
        # Webhook URL
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
        
        # Telegram API ga so'rov
        import requests
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": webhook_url}
        )
        
        return f"✅ Webhook o'rnatildi!<br>URL: {webhook_url}<br>Response: {response.text}"
        
    except Exception as e:
        return f"❌ Xatolik: {e}"

@app.route(f'/{os.getenv("BOT_TOKEN")}', methods=['POST'])
async def webhook():
    """Webhook handler - asosiy endpoint"""
    if bot_application is None:
        return "Bot not initialized", 500
    
    try:
        # JSON ma'lumotni olish
        json_data = request.get_json()
        
        # Update yaratish
        update = Update.de_json(json_data, bot_application.bot)
        
        # Update ni process qilish
        await bot_application.process_update(update)
        
        return "OK"
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

if __name__ == "__main__":
    # Botni setup qilish
    setup_bot()
    
    # Flask server ishga tushishi
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Flask server starting on port {port}")
    logger.info(f"🌐 Webhook URL: https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')}/{os.getenv('BOT_TOKEN')}")
    
    app.run(host='0.0.0.0', port=port, debug=False)