# keep_alive.py - FAQRAT keep-alive uchun
from flask import Flask
import threading
import time
import requests
import logging
from datetime import datetime

# Log qilishni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Moto.bike Bot is running! 🏍️"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/health')
def health():
    return "OK"

@app.route('/status')
def status():
    """UptimeRobot monitoring uchun status endpoint"""
    return {
        "status": "online",
        "bot": "running", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }, 200

@app.route('/keep-alive')
def keep_alive_endpoint():
    """Maxsus keep-alive endpoint"""
    return {"alive": True, "timestamp": datetime.now().isoformat()}, 200

@app.route('/awake')
def awake():
    """Uyg'onish uchun"""
    return "🔄 Bot uyg'on!", 200

def keep_awake():
    """1 daqiqa interval - OXIRGI URINISH"""
    while True:
        try:
            # BARCHA ASOSIY ENDPOINTLARNI TEKSHIRISH
            urls = [
                'https://moto-bike-jliv.onrender.com/',
                'https://moto-bike-jliv.onrender.com/ping',
                'https://moto-bike-jliv.onrender.com/health',
                'https://moto-bike-jliv.onrender.com/status',
                'https://moto-bike-jliv.onrender.com/keep-alive',
                'https://moto-bike-jliv.onrender.com/awake'
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, timeout=5)
                    logger.info(f"✅ {url.split('/')[-1]} - Status: {response.status_code}")
                except Exception as e:
                    logger.error(f"❌ {url}: {e}")
            
            logger.info("✅ Keep-alive cycle completed")
            
        except Exception as e:
            logger.error(f"❌ Keep-alive xatosi: {e}")
        
        # 1 DAQIQA (60 soniya) - MINIMUM
        time.sleep(60)

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("🚀 Starting keep-alive service...")
    
    # Flask server
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask server started")
    
    # Keep-alive
    threading.Thread(target=keep_awake, daemon=True).start()
    print("✅ Keep-alive started")
    
    # Cheksiz tsikla
    while True:
        time.sleep(60)