from flask import Flask
import threading
import time
import requests
import os

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
    """Botni 2 daqiqada bir uyg'otish"""
    while True:
        try:
            # Asosiy sahifani tekshirish
            response = requests.get('https://moto-bike.onrender.com/', timeout=10)
            if response.status_code == 200:
                print(f"✅ [{time.strftime('%H:%M:%S')}] Ping successful - Status: {response.status_code}")
            else:
                print(f"⚠️ [{time.strftime('%H:%M:%S')}] Ping status: {response.status_code}")
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] Ping failed: {e}")
        time.sleep(120)  # 2 daqiqa

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    print("🚀 Starting Flask server and keep-alive...")
    
    # Faqat Flask server
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ Flask server started")
    
    # Keep-alive
    threading.Thread(target=keep_awake, daemon=True).start()
    print("✅ Keep-alive started")
    
    # Botni ishga TUSHIRMAYMIZ!
    print("⚠️ Bot ishga tushirilmaydi - faqat Flask server ishlaydi")
    
    # Cheksiz tsikla
    while True:
        time.sleep(60)