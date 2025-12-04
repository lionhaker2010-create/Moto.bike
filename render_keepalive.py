# render_keepalive.py - Render uchun maxsus keep-alive
import threading
import time
import requests
import logging
import os

logger = logging.getLogger(__name__)

class RenderKeepAlive:
    def __init__(self):
        self.running = True
        self.url = f"http://localhost:{os.getenv('PORT', 8080)}"
        self.external_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', '')}"
    
    def start(self):
        """Keep-alive loop ni ishga tushirish"""
        thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        thread.start()
        logger.info("✅ Render keep-alive started")
        return thread
    
    def _keep_alive_loop(self):
        """Asosiy keep-alive loop"""
        while self.running:
            try:
                # 1. Local server ping
                response = requests.get(f"{self.url}/ping", timeout=5)
                if response.status_code == 200:
                    logger.debug("✅ Local ping successful")
                
                # 2. External ping (agar mavjud bo'lsa)
                if self.external_url and 'localhost' not in self.external_url:
                    try:
                        ext_response = requests.get(f"{self.external_url}/ping", timeout=10)
                        if ext_response.status_code == 200:
                            logger.debug("✅ External ping successful")
                    except:
                        pass
                
                # 3. Qo'shimcha health check
                requests.get(f"{self.url}/health", timeout=5)
                
            except Exception as e:
                logger.warning(f"⚠️ Keep-alive ping error: {e}")
            
            # 20-25 soniya oralig'ida ping yuborish
            time.sleep(20 + (time.time() % 5))  # 20-25 soniya oralig'ida
    
    def stop(self):
        """To'xtatish"""
        self.running = False

# Global instance
keep_alive = RenderKeepAlive()