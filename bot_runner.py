import os
import time
import logging
from threading import Thread
from flask import Flask

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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
    """Flask serverni ishga tushirish"""
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🔄 Flask server {port} portida ishga tushmoqda...")
    app.run(host='0.0.0.0', port=port)

def run_bot():
    """Botni ishga tushirish"""
    while True:
        try:
            logger.info("🤖 Bot ishga tushmoqda...")
            
            # Bot tokenini tekshirish
            TOKEN = os.getenv('BOT_TOKEN')
            if not TOKEN:
                logger.error("❌ BOT_TOKEN topilmadi! Environment variable ni tekshiring.")
                time.sleep(10)
                continue
            
            # Asosiy bot kodini import qilamiz
            from main import main
            main()
            
        except Exception as e:
            logger.error(f"❌ Botda xatolik: {e}")
            logger.info("🔄 Bot 10 soniyadan keyin qayta ishga tushadi...")
            time.sleep(10)

if __name__ == '__main__':
    logger.info("🚀 Bot runner ishga tushmoqda...")
    
    # Flask serverni background da ishga tushiramiz
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Botni ishga tushiramiz
    run_bot()