# server.py faylini quyidagicha qiling:
from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>🏍️ MotoBike Bot</title></head>
    <body style="text-align: center; padding: 50px; font-family: Arial;">
        <h1>🏍️ MotoBike Bot</h1>
        <p style="color: green; font-weight: bold;">✅ Status: Online va Faol</p>
        <p>Bot doimiy ishlayapti va hech qachon uxlamaydi!</p>
        <p><a href="/ping">🏓 Ping Test</a> | <a href="/health">📊 Health Check</a></p>
    </body>
    </html>
    """

@app.route('/ping')
def ping():
    return "🏓 pong"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "motobike-bot",
        "timestamp": time.time(),
        "port": os.environ.get("PORT", 8080)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Flask server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)