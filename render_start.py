import os
import time
import logging
from threading import Thread
from flask import Flask

# Log sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 MotoBike Bot ishlayapti! 🟢"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    """Botni ishga tushirish"""
    while True:
        try:
            from main import main
            main()
        except Exception as e:
            logger.error(f"Bot xatosi: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # Flask serverni ishga tushirish
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Botni ishga tushirish
    run_bot()