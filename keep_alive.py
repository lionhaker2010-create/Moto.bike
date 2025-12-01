from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🏍️ MotoBike Bot ishlayapti! Status: Online"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "motobike-bot"}

@app.route('/ping')
def ping():
    return "pong"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Serverni doimiy ishlab turish - Render uchun"""
    # Flask serverni background threadda ishga tushirish
    server = Thread(target=run_flask)
    server.daemon = True
    server.start()
    print("✅ Flask server ishga tushdi!")