# keep_alive.py o'rniga server.py ishlatamiz
# server.py faylini yarating:
from flask import Flask, render_template_string
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏍️ MotoBike Bot</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; 
                        backdrop-filter: blur(10px); }
            h1 { font-size: 2.5em; }
            .status { color: #4CAF50; font-weight: bold; font-size: 1.2em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏍️ MotoBike Bot</h1>
            <div class="status">✅ Status: Online va Faol</div>
            <p>Bot doimiy ishlayapti va hech qachon uxlamaydi!</p>
            <p><a href="/ping" style="color: #FF9800;">🏓 Ping Test</a></p>
        </div>
    </body>
    </html>
    ''')

@app.route('/ping')
def ping():
    return "🏓 pong"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "motobike-bot", "timestamp": time.time()}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Flask server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)