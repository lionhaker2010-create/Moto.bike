# keep_alive.py - FAQRAT keep-alive uchun
from flask import Flask
import threading
import time
import requests

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

def keep_awake():
    """Botni 5 daqiqada bir uyg'otish - RENDER UCHUN OPTIMALLASHTIRILGAN"""
    while True:
        try:
            # BARCHA ENDPOINTLARNI TEKSHIRISH
            endpoints = [
                '/', '/ping', '/health', '/status', '/monitoring'
            ]
            
            for endpoint in endpoints:
                try:
                    url = f'https://moto-bike-jliv.onrender.com{endpoint}'
                    response = requests.get(url, timeout=10)
                    logger.info(f"✅ {endpoint} - Status: {response.status_code}")
                except Exception as e:
                    logger.error(f"❌ {endpoint}: {e}")
            
            # QO'SHIMCHA: Botning o'zini tekshirish
            try:
                bot_status = requests.get('https://moto-bike-jliv.onrender.com/status', timeout=5)
                if bot_status.status_code == 200:
                    logger.info("🤖 Bot status: ONLINE")
            except:
                logger.warning("⚠️ Bot status check failed")
                    
        except Exception as e:
            logger.error(f"❌ Keep-alive xatosi: {e}")
        
        # 5 DAQIQA - RENDER FREE UCHUN OPTIMAL
        time.sleep(300)