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

# ... (HTML_TEMPLATE va boshqa funksiyalar o'zgarmaydi) ...

# ==================== YANGI: RENDER UCHUN MAXSUS FUNKSIYALAR ====================
def ping_self():
    """O'zimizga ping yuborish (Render uchun maxsus)"""
    try:
        port = os.environ.get('PORT', 8080)
        url = f"http://localhost:{port}/ping"
        
        # 3 marta urinib ko'rish
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Self-ping successful (attempt {attempt + 1})")
                    return True
            except Exception as e:
                logger.warning(f"⚠️ Self-ping attempt {attempt + 1} failed: {e}")
                time.sleep(5)
        
        logger.error("❌ All self-ping attempts failed")
        return False
    except Exception as e:
        logger.error(f"❌ Ping self error: {e}")
        return False

def ping_render():
    """Render'ning asosiy URL ga ping yuborish"""
    try:
        render_url = os.getenv('RENDER_URL', 'https://motobike-bot.onrender.com')
        if not render_url.startswith('http'):
            render_url = f"https://{render_url}"
        
        response = requests.get(f"{render_url}/ping", timeout=15)
        if response.status_code == 200:
            logger.info(f"✅ Render ping successful: {render_url}")
            return True
        else:
            logger.warning(f"⚠️ Render ping status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Render ping error: {e}")
        return False

# ==================== YANGI: KUCHLIROQ KEEP-ALIVE LOOP ====================
def start_keep_alive_loop():
    """Kuchli keep-alive loop"""
    import threading
    
    def keep_alive_worker():
        counter = 0
        while True:
            counter += 1
            try:
                logger.info(f"🔄 Keep-alive cycle #{counter}")
                
                # 1. O'zimizga ping
                self_success = ping_self()
                
                # 2. Render'ga ping (har 3-chi aylanishda)
                if counter % 3 == 0:
                    render_success = ping_render()
                
                # 3. Har 5 daqiqada (300 soniya)
                time.sleep(300)  # 5 daqiqa
                
            except Exception as e:
                logger.error(f"❌ Keep-alive loop error: {e}")
                time.sleep(60)  # Xatolik bo'lsa 1 daqiqa kutish
    
    # Thread ni ishga tushirish
    thread = threading.Thread(target=keep_alive_worker, daemon=True)
    thread.start()
    logger.info("✅ Keep-alive loop started")
    return thread

# ==================== SERVER ISHGA TUSHIRISH ====================
def start_server():
    """Serverni ishga tushirish"""
    port = int(os.environ.get('PORT', 8080))
    
    # DEBUG ma'lumotlari
    logger.info(f"🚀 Flask server ishga tushmoqda...")
    logger.info(f"🌐 Port: {port}")
    logger.info(f"📡 Host: 0.0.0.0")
    logger.info(f"⚡ RENDER: {os.getenv('RENDER', 'False')}")
    
    try:
        # YANGI: Development mode o'chirish
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False, 
            threaded=True,
            use_reloader=False  # ✅ Muhim: Reloader o'chirish
        )
        logger.info("✅ Flask server muvaffaqiyatli ishga tushdi!")
    except Exception as e:
        logger.error(f"❌ Flask server ishga tushirishda xatolik: {e}")

# ==================== ASOSIY FUNKSIYA ====================
def keep_alive():
    """Serverni doimiy ishlab turish"""
    # Flask serverni background threadda ishga tushirish
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    logger.info("✅ Flask server ishga tushdi!")
    logger.info(f"🌐 Web interface is ready")
    
    # Keep-alive loop ni ishga tushirish
    keep_alive_thread = start_keep_alive_loop()
    
    # Render uchun qo'shimcha: main thread ni bloklash
    try:
        while True:
            time.sleep(3600)  # Har soat
            logger.info("⏰ Keep-alive system is still running...")
    except KeyboardInterrupt:
        logger.info("🛑 Keep-alive system stopped")

# Agar to'g'ridan-to'g'ri ishga tushirilsa
if __name__ == '__main__':
    keep_alive()