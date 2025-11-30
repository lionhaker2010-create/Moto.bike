# keep_alive.py - KINO BOT USULIDA
from flask import Flask
from threading import Thread
import time
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Moto.bike Bot is running! ✅"

@app.route('/health')
def health():
    return "🟢 OK"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/status')
def status():
    return {"status": "online", "service": "Moto.bike Bot"}, 200

def run():
    port = int(os.environ.get("PORT", 10000))  # ✅ 10000 PORT
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    server = Thread(target=run)
    server.start()

def start_pinging():
    print("🔄 MotoBot Auto-ping service started!")
    
    # ✅ TO'G'RI URL
    render_url = 'https://moto-bike-jliv.onrender.com'
    
    while True:
        try:
            # FAQAT 2 TA ASOSIY ENDPOINT
            requests.get(f"{render_url}/", timeout=5)
            requests.get(f"{render_url}/health", timeout=5)
            print(f"✅ MotoBot Ping successful - {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ MotoBot Ping failed: {e}")
        
        time.sleep(600)  # ✅ 10 DAQIQA - KINO BOT USULI

def start_background_ping():
    ping_thread = Thread(target=start_pinging, daemon=True)
    ping_thread.start()