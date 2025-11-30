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
    """Botni 1 daqiqada bir uyg'otish"""
    while True:
        try:
            # ✅ URL ni yangilang (sizning haqiqiy URL)
            response = requests.get('https://moto-bike-jliv.onrender.com/ping', timeout=10)
            logger.info(f"✅ Ping successful - Status: {response.status_code}")
            
            # ✅ Monitoring check qo'shish (agar mavjud bo'lsa)
            if bot_monitor:
                bot_monitor.check_bot_health()
                
        except Exception as e:
            logger.error(f"❌ Ping failed: {e}")
        time.sleep(60)  # 1 daqiqa