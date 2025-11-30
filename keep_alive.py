from flask import Flask
from threading import Thread
import time
import os
import logging

# Log sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 MotoBike Bot ishlayapti! Status: Online 🟢"

@app.route('/health')
def health():
    return "OK"

@app.route('/ping')
def ping():
    return "PONG"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Serverni doimiy ishlab turish"""
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    logger.info(f"🔄 Keep-alive server {os.environ.get('PORT', 8080)} portida ishga tushdi...")

if __name__ == '__main__':
    keep_alive()
    
    # Asosiy botni alohida processda ishga tushiramiz
    try:
        logger.info("🤖 Bot ishga tushmoqda...")
        # Botni alohida import qilamiz
        from main import main_bot
        main_bot()
    except Exception as e:
        logger.error(f"❌ Bot ishga tushmadi: {e}")
        logger.info("🔄 Qayta urinilmoqda...")
        time.sleep(10)