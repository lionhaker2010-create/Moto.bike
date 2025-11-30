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

def keep_awake():
    """Botni 2 daqiqada bir uyg'otish"""
    while True:
        try:
            # 3 xil URL ga so'rov yuboramiz
            requests.get('https://moto-bike.onrender.com/', timeout=5)
            requests.get('https://moto-bike.onrender.com/ping', timeout=5) 
            print(f"✅ [{time.strftime('%H:%M:%S')}] Ping successful")
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] Ping failed: {e}")
        time.sleep(120)  # 2 daqiqa

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Flask server
    t1 = threading.Thread(target=run_flask)
    t1.daemon = True
    t1.start()
    
    # Self-ping
    t2 = threading.Thread(target=keep_awake)
    t2.daemon = True
    t2.start()

if __name__ == '__main__':
    keep_alive()
    # Botni ishga tushirish
    from main import main
    main()