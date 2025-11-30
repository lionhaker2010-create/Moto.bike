import threading
import time
import requests
import os

def keep_awake():
    """Botni 2 daqiqada bir uyg'otish"""
    while True:
        try:
            response = requests.get('https://moto-bike.onrender.com/', timeout=10)
            print(f"✅ [{time.strftime('%H:%M:%S')}] Ping successful - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] Ping failed: {e}")
        time.sleep(120)  # 2 daqiqa

def start_bot():
    """Botni ishga tushirish"""
    from main import main
    main()

if __name__ == '__main__':
    # Background ping ni boshlash
    ping_thread = threading.Thread(target=keep_awake)
    ping_thread.daemon = True
    ping_thread.start()
    print("🔄 Keep-alive started")
    
    # Botni ishga tushirish
    start_bot()