# monitoring.py - Advanced monitoring
import time
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BotMonitor:
    def __init__(self, bot_url):
        self.bot_url = bot_url
        self.last_check = None
        self.uptime_count = 0
        self.downtime_count = 0
        
    def check_bot_health(self):
        """Bot holatini tekshirish"""
        try:
            start_time = time.time()
            
            # Asosiy sahifani tekshirish
            response = requests.get(f"{self.bot_url}/", timeout=10)
            main_status = response.status_code == 200
            
            # Health check
            health_response = requests.get(f"{self.bot_url}/health", timeout=5)
            health_status = health_response.status_code == 200
            
            # Status check
            status_response = requests.get(f"{self.bot_url}/status", timeout=5)
            status_data = status_response.json() if status_response.status_code == 200 else {}
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            self.last_check = datetime.now()
            
            if main_status and health_status:
                self.uptime_count += 1
                logger.info(f"✅ Bot healthy - Response: {response_time:.2f}ms")
                return True
            else:
                self.downtime_count += 1
                logger.error(f"❌ Bot unhealthy - Main: {main_status}, Health: {health_status}")
                return False
                
        except Exception as e:
            self.downtime_count += 1
            logger.error(f"❌ Bot check failed: {e}")
            return False
    
    def get_stats(self):
        """Statistikani olish"""
        total_checks = self.uptime_count + self.downtime_count
        uptime_percentage = (self.uptime_count / total_checks * 100) if total_checks > 0 else 0
        
        return {
            "uptime_count": self.uptime_count,
            "downtime_count": self.downtime_count,
            "uptime_percentage": f"{uptime_percentage:.2f}%",
            "last_check": self.last_check.isoformat() if self.last_check else "Never",
            "total_checks": total_checks
        }

# Global monitor
bot_monitor = BotMonitor("https://moto-bike-jliv.onrender.com")