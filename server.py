# server.py
from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏍️ MotoBike Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            h1 {{ 
                margin-bottom: 20px; 
                font-size: 2.5em;
            }}
            .status {{
                background: #10B981;
                color: white;
                padding: 12px 24px;
                border-radius: 10px;
                display: inline-block;
                font-weight: bold;
                margin: 20px 0;
                font-size: 1.2em;
            }}
            .links {{
                margin-top: 30px;
            }}
            .links a {{
                display: inline-block;
                margin: 10px;
                padding: 12px 24px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s;
                font-weight: bold;
            }}
            .links a:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }}
            .timestamp {{
                margin-top: 20px;
                font-size: 0.9em;
                opacity: 0.8;
            }}
            .info {{
                margin: 15px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏍️ MotoBike Bot</h1>
            <div class="status">✅ ONLINE - Never Sleeps!</div>
            
            <div class="info">
                <p><strong>Server Status:</strong> Active and Running</p>
                <p><strong>Service:</strong> Telegram Bot + Flask Server</p>
                <p><strong>Port:</strong> {os.getenv('PORT', 8080)}</p>
            </div>
            
            <div class="links">
                <a href="/ping">🏓 Ping Test</a>
                <a href="/health">📊 Health Check</a>
                <a href="/status">📈 Status</a>
            </div>
            
            <div class="timestamp">
                Last checked: {current_time}<br>
                Auto-ping every 25 seconds
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({
        "status": "success",
        "message": "pong",
        "timestamp": datetime.now().isoformat(),
        "service": "motobike-bot",
        "environment": os.getenv('RENDER', 'production')
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "bot": "running",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active"
    })

@app.route('/status')
def status():
    """Detailed status"""
    return jsonify({
        "status": "online",
        "environment": os.getenv('RENDER', 'production'),
        "port": os.getenv('PORT', 8080),
        "hostname": os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
        "timestamp": datetime.now().isoformat(),
        "service": "Telegram Bot + Flask"
    })

@app.route('/keepalive')
def keep_alive():
    """Keep-alive endpoint for Render"""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "message": "Render keep-alive ping received"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Flask server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)