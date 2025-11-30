from flask import Flask
import threading
import time
import urllib.request
import urllib.error

app = Flask(__name__)

@app.route('/')
def home():
    return "Moto.bike Bot is running! 🏍️"

@app.route('/ping')
def ping():
    return "pong"

def keep_awake():
    """Botni 2 daqiqada bir uyg'otish (requests siz)"""
    while True:
        try:
            # urllib yordamida ping qilish
            with urllib.request.urlopen('https://moto-bike.onrender.com/ping', timeout=10) as response:
                if response.getcode() == 200:
                    print(f"✅ [{time.strftime('%H:%M:%S')}] Ping successful")
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