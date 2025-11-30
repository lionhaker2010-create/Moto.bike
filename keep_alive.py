from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🏍️ MotoBike Bot ishlayapti! Status: Online"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "motobike-bot"}

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Serverni doimiy ishlab turish - Render uchun"""
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()