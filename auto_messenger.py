# auto_messenger.py - Kuniga 3 marta avtomatik xabar yuborish
import os
import time
import threading
import logging
import schedule
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class AutoMessenger:
    def __init__(self, bot_token, db):
        self.bot_token = bot_token
        self.db = db
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.running = False
        self.tashkent_tz = pytz.timezone('Asia/Tashkent')
        
    def get_tashkent_time(self):
        """Toshkent vaqtini olish"""
        return datetime.now(self.tashkent_tz)
    
    def send_message_to_user(self, user_id, message):
        """Bitta foydalanuvchiga xabar yuborish"""
        try:
            import requests
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": user_id,
                    "text": message,
                    "parse_mode": "HTML"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Xabar yuborildi: user_id={user_id}")
                return True
            else:
                logger.error(f"❌ Xabar yuborishda xatolik: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Xabar yuborishda xatolik user_id={user_id}: {e}")
            return False
    
    def send_morning_message(self):
        """Ertalabki xabar (8:00)"""
        logger.info("🕗 8:00 - Ertalabki xabar yuborilmoqda...")
        message = """
<b>☀️ Assalomu alaykum! Xayrli tong!</b>

🏍️ <b>MotoBike Bot</b> bilan yangi kuningiz muborak bo‘lsin!

📦 <b>Bugun nima buyurtma qilamiz?</b>
• Moto ehtiyot qismlari
• Scooter qismlari  
• Electric Scooter arenda

📞 <b>Qo'llab-quvvatlash:</b> @Operator_Kino_1985
☎️ <b>Telefon:</b> +998(98)8882505

🕒 <b>Ish vaqti:</b> 09:00 - 18:00
        """
        self.send_broadcast(message)
    
    def send_afternoon_message(self):
        """Tushki xabar (14:00)"""
        logger.info("🕑 14:00 - Tushki xabar yuborilmoqda...")
        message = """
<b>🕑 Hayrli kun!</b>

⚡ <b>Kunning ikkinchi yarmida ham biz bilan!</b>

🎯 <b>Maxsus taklif:</b>
• Har qanday moto ehtiyot qismlari
• Tez yetkazib berish
• Sifat kafolati

📦 <b>Buyurtma berish uchun:</b>
1. Kategoriyani tanlang
2. Mahsulotni tanlang  
3. Yetkazib berish manzilini yuboring

🔥 <b>Bugun 10 ta buyurtma chegirma bilan!</b>
        """
        self.send_broadcast(message)
    
    def send_evening_message(self):
        """Kechki xabar (20:00)"""
        logger.info("🕗 20:00 - Kechki xabar yuborilmoqda...")
        message = """
<b>🌙 Hayrli kech! Kunning yakuni muborak!</b>

📊 <b>Bugungi statistika:</b>
• {} ta yangi buyurtma
• {} ta mamnun mijoz
• 100% sifat kafolati

🎁 <b>Ertangi kun uchun sovg'a:</b>
Har 5-buyurtmaga <b>10% chegirma!</b>

📞 <b>24/7 qo'llab-quvvatlash:</b>
@Operator_Kino_1985
+998(98)8882505

<b>Yaxshi dam oling! Ertaga yana ko'rishguncha! 👋</b>
        """.format(
            len(self.db.get_orders()),  # Bugungi buyurtmalar soni
            len(self.db.get_all_users())  # Jami foydalanuvchilar
        )
        self.send_broadcast(message)
    
    def send_broadcast(self, message):
        """Barcha foydalanuvchilarga xabar yuborish"""
        try:
            users = self.db.get_all_users()
            total = len(users)
            successful = 0
            
            logger.info(f"📤 {total} ta foydalanuvchiga xabar yuborilmoqda...")
            
            for user in users:
                user_id = user[0]  # user_id maydoni
                
                # Faqat ro'yxatdan o'tgan foydalanuvchilarga
                if len(user) > 5 and user[5]:  # registered = TRUE
                    if self.send_message_to_user(user_id, message):
                        successful += 1
                
                # Har 10 ta xabardan keyin biroz kutish (rate limit uchun)
                if successful % 10 == 0:
                    time.sleep(0.5)
            
            logger.info(f"✅ Xabar yuborish yakunlandi: {successful}/{total}")
            
        except Exception as e:
            logger.error(f"❌ Broadcast xabar yuborishda xatolik: {e}")
    
    def schedule_messages(self):
        """Xabarlarni vaqt jadvaliga qo'yish"""
        # Toshkent vaqti bilan
        schedule.every().day.at("08:00").do(self.send_morning_message)
        schedule.every().day.at("14:00").do(self.send_afternoon_message)
        schedule.every().day.at("20:00").do(self.send_evening_message)
        
        logger.info("📅 Xabar jadvali o'rnatildi: 8:00, 14:00, 20:00 (Toshkent vaqti)")
        
        # Jadvalni tekshirish loop'i
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Har daqiqa tekshirish
    
    def start(self):
        """Messenger ni ishga tushirish"""
        self.running = True
        
        # Dastlabki holatni tekshirish
        tashkent_time = self.get_tashkent_time()
        logger.info(f"🕐 Toshkent vaqti: {tashkent_time.strftime('%H:%M:%S')}")
        
        # Jadvalni sozlash
        thread = threading.Thread(target=self.schedule_messages, daemon=True)
        thread.start()
        
        logger.info("✅ Auto-messenger ishga tushirildi")
        return thread
    
    def stop(self):
        """To'xtatish"""
        self.running = False
        logger.info("🛑 Auto-messenger to'xtatildi")

# Global instance
auto_messenger = None