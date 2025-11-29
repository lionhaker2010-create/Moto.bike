from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "MotoBike Bot ishlayapti!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Serverni doimiy ishlab turish"""
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

if __name__ == '__main__':
    keep_alive()
    # Asosiy bot kodini bu yerda ishga tushiring