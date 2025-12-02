from flask import Flask, render_template_string
from threading import Thread
import os
import time
import requests
import logging

app = Flask(__name__)

# Log qilish
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🏍️ MotoBike Bot</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        h1 {
            font-size: 3em;
            margin-bottom: 20px;
        }
        .status {
            font-size: 1.5em;
            color: #4CAF50;
            font-weight: bold;
        }
        .stats {
            margin-top: 30px;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏍️ MotoBike Bot</h1>
        <div class="status">✅ Status: Online va Faol</div>
        <p>Bot doimiy ishlayapti va hech qachon uxlamaydi!</p>
        
        <div class="stats">
            <p>🚀 <strong>Ishga tushirilgan:</strong> {{ start_time }}</p>
            <p>⏰ <strong>Ish vaqti:</strong> {{ uptime }}</p>
            <p>🔧 <strong>Versiya:</strong> 2.0</p>
            <p>📊 <strong>Holat:</strong> To'liq ishlayapti</p>
        </div>
        
        <div style="margin-top: 40px;">
            <a href="/health" style="color: #4CAF50; text-decoration: none; font-weight: bold;">📊 Health Check</a> | 
            <a href="/ping" style="color: #FF9800; text-decoration: none; font-weight: bold;">🏓 Ping Test</a> |
            <a href="/restart" style="color: #f44336; text-decoration: none; font-weight: bold;">🔄 Restart</a>
        </div>
    </div>
</body>
</html>
"""

start_time = time.time()

def get_uptime():
    """Ish vaqtini hisoblash"""
    uptime_seconds = int(time.time() - start_time)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    if days > 0:
        return f"{days} kun, {hours} soat, {minutes} daqiqa"
    elif hours > 0:
        return f"{hours} soat, {minutes} daqiqa, {seconds} soniya"
    else:
        return f"{minutes} daqiqa, {seconds} soniya"

@app.route('/')
def home():
    """Asosiy sahifa"""
    return render_template_string(
        HTML_TEMPLATE,
        start_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
        uptime=get_uptime()
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "motobike-bot",
        "timestamp": time.time(),
        "uptime": get_uptime(),
        "version": "2.0"
    }

@app.route('/ping')
def ping():
    """Ping test"""
    return "🏓 pong"

@app.route('/restart')
def restart():
    """Botni restart qilish"""
    # Bu faqat simulyatsiya, haqiqiy restart uchun Render dashboard ishlatiladi
    return "🔄 Botni restart qilish uchun Render dashboard ga o'ting"

@app.route('/keep-alive')
def keep_alive():
    """Keep alive endpoint - boshqa serverlarga ping"""
    try:
        # O'zimizga ping yuboramiz
        requests.get(f"http://localhost:{os.environ.get('PORT', 8080)}/ping", timeout=5)
        return "✅ Keep-alive ishlayapti"
    except:
        return "⚠️ Keep-alive da muammo"

def start_server():
    """Serverni ishga tushirish"""
    port = int(os.environ.get('PORT', 8080))
    
    # DEBUG ma'lumotlari
    logger.info(f"🚀 Flask server ishga tushmoqda...")
    logger.info(f"🌐 Port: {port}")
    logger.info(f"📡 Host: 0.0.0.0")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        logger.info("✅ Flask server muvaffaqiyatli ishga tushdi!")
    except Exception as e:
        logger.error(f"❌ Flask server ishga tushirishda xatolik: {e}")

def keep_alive():
    """Serverni doimiy ishlab turish"""
    # Flask serverni background threadda ishga tushirish
    server = Thread(target=start_server)
    server.daemon = True
    server.start()
    
    logger.info("✅ Flask server ishga tushdi!")
    logger.info("🌐 Web interface: https://[your-render-url].onrender.com")
    
    # Keep-alive loop
    keep_alive_thread = Thread(target=keep_alive_loop)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

def keep_alive_loop():
    """Doimiy ping yuborish"""
    import time
    
    while True:
        try:
            # Har 5 daqiqada o'zimizga ping yuboramiz
            time.sleep(300)  # 5 daqiqa
            
            # O'zimizga ping
            port = os.environ.get('PORT', 8080)
            try:
                response = requests.get(f"http://localhost:{port}/ping", timeout=10)
                if response.status_code == 200:
                    logger.info("🔄 Keep-alive ping muvaffaqiyatli")
                else:
                    logger.warning(f"⚠️ Keep-alive ping: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Keep-alive ping xatolik: {e}")
                
        except Exception as e:
            logger.error(f"Keep-alive loop xatolik: {e}")
            time.sleep(60)

# Serverni ishga tushirish
if __name__ == '__main__':
    keep_alive()
    # Asosiy threadni bloklash
    while True:
        time.sleep(3600)  # Har soatda bir marta