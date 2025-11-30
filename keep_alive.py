from flask import Flask
from threading import Thread
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 MotoBike Bot ishlayapti! Status: Online"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Serverni doimiy ishlab turish"""
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

if __name__ == '__main__':
    keep_alive()
    print("🔄 Keep-alive server ishga tushdi...")
    # Asosiy botni ishga tushirish
    try:
        from main import main
        main()
    except Exception as e:
        print(f"❌ Bot ishga tushmadi: {e}")
        time.sleep(5)