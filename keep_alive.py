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
    return {"status": "healthy", "service": "Moto.bike Bot"}

def keep_awake():
    """Botni 2 daqiqada bir uyg'otish"""
    while True:
        try:
            # 3 xil URL ni tekshiramiz
            requests.get('https://moto-bike.onrender.com/', timeout=5)
            requests.get('https://moto-bike.onrender.com/ping', timeout=5)
            requests.get('https://moto-bike.onrender.com/health', timeout=5)
            print(f"✅ [{time.strftime('%H:%M:%S')}] All pings successful")
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] Ping failed: {e}")
        time.sleep(120)  # 2 daqiqa

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Flask server
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Self-ping
    threading.Thread(target=keep_awake, daemon=True).start()
    
    # Botni ishga tushirish
    from main import main
    main()