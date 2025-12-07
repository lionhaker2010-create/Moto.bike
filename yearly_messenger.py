# yearly_messenger.py - 2025-2026 12 oy uchun avtomatik xabarlar
import os
import time
import threading
import logging
import schedule
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class YearlyMessenger:
    def __init__(self, bot_token, db):
        self.bot_token = bot_token
        self.db = db
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.running = False
        self.tashkent_tz = pytz.timezone('Asia/Tashkent')
        
        # 2025-2026 yillar uchun xabarlar
        self.yearly_messages = self.load_yearly_messages()
        
        # Xabarlarni faylga saqlash
        self.messages_file = Path('/data/messages.json') if 'RENDER' in os.environ else Path('messages.json')
        self.save_messages_to_file()
    
    def load_yearly_messages(self):
        """2025-2026 yillar uchun xabarlarni yuklash"""
        messages = {
            '2025': {
                '12': self.get_december_2025_messages()  # Dekabr 2025
            },
            '2026': {
                '01': self.get_january_2026_messages(),   # Yanvar 2026
                '02': self.get_february_2026_messages(),  # Fevral 2026
                '03': self.get_march_2026_messages(),     # Mart 2026
                '04': self.get_april_2026_messages(),     # Aprel 2026
                '05': self.get_may_2026_messages(),       # May 2026
                '06': self.get_june_2026_messages(),      # Iyun 2026
                '07': self.get_july_2026_messages(),      # Iyul 2026
                '08': self.get_august_2026_messages(),    # Avgust 2026
                '09': self.get_september_2026_messages(), # Sentabr 2026
                '10': self.get_october_2026_messages(),   # Oktabr 2026
                '11': self.get_november_2026_messages(),  # Noyabr 2026
                '12': self.get_december_2026_messages()   # Dekabr 2026
            }
        }
        return messages
    
    def save_messages_to_file(self):
        """Xabarlarni faylga saqlash"""
        try:
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(self.yearly_messages, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Xabarlar faylga saqlandi: {self.messages_file}")
        except Exception as e:
            logger.error(f"❌ Xabarlarni saqlashda xatolik: {e}")
    
    def get_tashkent_time(self):
        """Toshkent vaqtini olish"""
        return datetime.now(self.tashkent_tz)
    
    def get_current_month_year(self):
        """Joriy oy va yilni olish"""
        now = self.get_tashkent_time()
        return now.year, now.strftime('%m')
    
    def get_user_language(self, user_id):
        """Foydalanuvchi tilini olish"""
        try:
            user = self.db.get_user(user_id)
            if user and len(user) > 4:
                return user[4]  # language maydoni
            return 'uz'  # default
        except:
            return 'uz'
    
    def get_message_for_date(self, message_type, year, month, day=None, language='uz'):
        """Berilgan sana uchun xabar olish"""
        try:
            year_str = str(year)
            month_str = str(month).zfill(2)
            
            # Oylik xabarlar
            month_messages = self.yearly_messages.get(year_str, {}).get(month_str, {})
            
            if not month_messages:
                # Agar oy uchun xabar yo'q bo'lsa, umumiy xabar
                return self.get_general_message(message_type, language)
            
            # Kunlik maxsus xabarlar (bayramlar uchun)
            if day:
                day_key = f"{month_str}_{day:02d}"
                day_message = month_messages.get('special_days', {}).get(day_key, {}).get(language)
                if day_message:
                    return day_message
            
            # Oddiy kun xabari
            return month_messages.get(message_type, {}).get(language, self.get_general_message(message_type, language))
            
        except Exception as e:
            logger.error(f"❌ Xabar olishda xatolik: {e}")
            return self.get_general_message(message_type, language)
    
    def get_general_message(self, message_type, language='uz'):
        """Umumiy xabar"""
        general = {
            'uz': {
                'morning': "☀️ Xayrli tong! Yangi kunningiz muborak!",
                'afternoon': "🕑 Hayrli kun! Ishotingiz omadli o'tsin!",
                'evening': "🌙 Hayrli kech! Yaxshi dam oling!"
            },
            'ru': {
                'morning': "☀️ Доброе утро! Хорошего дня!",
                'afternoon': "🕑 Добрый день! Удачи в работе!",
                'evening': "🌙 Добрый вечер! Хорошего отдыха!"
            },
            'en': {
                'morning': "☀️ Good morning! Have a nice day!",
                'afternoon': "🕑 Good afternoon! Good luck with work!",
                'evening': "🌙 Good evening! Have a good rest!"
            }
        }
        return general.get(language, general['uz']).get(message_type, "🏍️ MotoBike Bot")
    
    # ==================== 2025-2026 YILLAR XABARLARI ====================
    
    def get_december_2025_messages(self):
        """Dekabr 2025 - Yangi yilga tayyorgarlik"""
        return {
            'uz': {
                'morning': "☀️ Dekabr 2025! Yangi yilga tayyorgarlik boshlang! 🎄",
                'afternoon': "🕑 Yangi yil oldidan maxsus takliflar! 🎁",
                'evening': "🌙 Kechki statistika: {} ta buyurtma, {} ta mijoz"
            },
            'ru': {
                'morning': "☀️ Декабрь 2025! Начинаем готовиться к Новому году! 🎄",
                'afternoon': "🕑 Специальные предложения перед Новым годом! 🎁",
                'evening': "🌙 Вечерняя статистика: {} заказов, {} клиентов"
            },
            'en': {
                'morning': "☀️ December 2025! Start preparing for New Year! 🎄",
                'afternoon': "🕑 Special offers before New Year! 🎁",
                'evening': "🌙 Evening statistics: {} orders, {} customers"
            },
            'special_days': {
                '12_31': {  # Yangi yil arvohi
                    'uz': "🎉 Yangi yil arvohi! 2026 ga kirishga soatlar qoldi! 🥳",
                    'ru': "🎉 Канун Нового года! Часы до 2026 года! 🥳", 
                    'en': "🎉 New Year's Eve! Hours until 2026! 🥳"
                }
            }
        }
    
    def get_january_2026_messages(self):
        """Yanvar 2026 - Yangi yil, yangi imkoniyatlar"""
        return {
            'uz': {
                'morning': "☀️ Yangi yil 2026 muborak! 🎊 Yanvar oyida yangi imkoniyatlar!",
                'afternoon': "🕑 Yanvar chegirmalari: -15% barcha mahsulotlarda! ❄️",
                'evening': "🌙 Yanvar oyi: {} ta yangi mijoz, {} ta buyurtma"
            },
            'ru': {
                'morning': "☀️ С Новым 2026 годом! 🎊 Новые возможности в январе!",
                'afternoon': "🕑 Январские скидки: -15% на все товары! ❄️",
                'evening': "🌙 Январь: {} новых клиентов, {} заказов"
            },
            'en': {
                'morning': "☀️ Happy New Year 2026! 🎊 New opportunities in January!",
                'afternoon': "🕑 January discounts: -15% on all products! ❄️",
                'evening': "🌙 January: {} new customers, {} orders"
            },
            'special_days': {
                '01_01': {  # Yangi yil
                    'uz': "🎉 Yangi yilingiz muborak 2026! 🥂 Yangi imkoniyatlar sizni kutmoqda!",
                    'ru': "🎉 С Новым 2026 годом! 🥂 Новые возможности ждут вас!",
                    'en': "🎉 Happy New Year 2026! 🥂 New opportunities await you!"
                },
                '01_14': {  # Yangi yil (eski usul)
                    'uz': "🎄 Eski usul bo'yicha Yangi yil! Ikkita bayram!",
                    'ru': "🎄 Старый Новый год! Два праздника!", 
                    'en': "🎄 Old New Year! Two holidays!"
                }
            }
        }
    
    def get_february_2026_messages(self):
        """Fevral 2026 - Sevgililar kuni va qish fasli"""
        return {
            'uz': {
                'morning': "❤️ Fevral - Sevgi va mehr oyi! Sevgililar kuni uchun sovg'alar!",
                'afternoon': "🕑 Fevral chegirmalari: Maxsus sevgi paketlari -20%! 💝",
                'evening': "🌙 Fevral statistika: {} ta sevgi sovg'asi, {} ta baxtli mijoz"
            },
            'ru': {
                'morning': "❤️ Февраль - месяц любви и нежности! Подарки на День влюбленных!",
                'afternoon': "🕑 Февральские скидки: Специальные любовные пакеты -20%! 💝",
                'evening': "🌙 Февральская статистика: {} любовных подарков, {} счастливых клиентов"
            },
            'en': {
                'morning': "❤️ February - Month of love and tenderness! Gifts for Valentine's Day!",
                'afternoon': "🕑 February discounts: Special love packages -20%! 💝",
                'evening': "🌙 February statistics: {} love gifts, {} happy customers"
            },
            'special_days': {
                '02_14': {  # Sevgililar kuni
                    'uz': "💝 Sevgililar kuni muborak! Sizning sevgingiz abadiy! ❤️",
                    'ru': "💝 С Днем святого Валентина! Ваша любовь вечна! ❤️",
                    'en': "💝 Happy Valentine's Day! Your love is eternal! ❤️"
                },
                '02_23': {  # Vatan himoyachilari kuni
                    'uz': "🪖 Vatan himoyachilari kuni! Hurmatli erkaklar, tabriklaymiz!",
                    'ru': "🪖 День защитника Отечества! Уважаемые мужчины, поздравляем!",
                    'en': "🪖 Defender of the Fatherland Day! Dear men, congratulations!"
                }
            }
        }
    
    def get_march_2026_messages(self):
        """Mart 2026 - Bahor, Xalqaro ayollar kuni, Navro'z"""
        return {
            'uz': {
                'morning': "🌸 Mart - Bahor kelishi! Tabiat uyg'onadi, biz ham!",
                'afternoon': "🕑 Bahor chegirmalari: Yangi mavsum uchun yangi qismlar! 🌱",
                'evening': "🌙 Bahor statistikasi: {} ta bahorgi buyurtma, {} ta yangi mijoz"
            },
            'ru': {
                'morning': "🌸 Март - Приход весны! Природа просыпается, и мы тоже!",
                'afternoon': "🕑 Весенние скидки: Новые детали для нового сезона! 🌱",
                'evening': "🌙 Весенняя статистика: {} весенних заказов, {} новых клиентов"
            },
            'en': {
                'morning': "🌸 March - Arrival of spring! Nature awakens, and so do we!",
                'afternoon': "🕑 Spring discounts: New parts for new season! 🌱",
                'evening': "🌙 Spring statistics: {} spring orders, {} new customers"
            },
            'special_days': {
                '03_08': {  # Xalqaro ayollar kuni
                    'uz': "👩‍🦰 Xalqaro ayollar kuni muborak! Siz dunyoning yarmisiz! 💐",
                    'ru': "👩‍🦰 С Международным женским днем! Вы - половина мира! 💐",
                    'en': "👩‍🦰 Happy International Women's Day! You are half the world! 💐"
                },
                '03_21': {  # Navro'z
                    'uz': "🌿 Navro'z muborak! Yangi yil, yangi umidlar! 🎉",
                    'ru': "🌿 С Наврузом! Новый год, новые надежды! 🎉",
                    'en': "🌿 Happy Nowruz! New year, new hopes! 🎉"
                }
            }
        }
    
    def get_april_2026_messages(self):
        """Aprel 2026 - Bahor to'liq kuchida"""
        return {
            'uz': {
                'morning': "🌷 Aprel - Bahor to'liq kuchida! Sayohat va sayr qilish mavsumi!",
                'afternoon': "🕑 Aprel takliflari: Sayohat uchun moto aksessuarlari! 🏍️",
                'evening': "🌙 Aprel oyi: {} ta sayohatchi, {} ta yo'lchi mijoz"
            },
            'ru': {
                'morning': "🌷 Апрель - Весна в полную силу! Сезон путешествий и прогулок!",
                'afternoon': "🕑 Апрельские предложения: Мото аксессуары для путешествий! 🏍️",
                'evening': "🌙 Апрель: {} путешественников, {} дорожных клиентов"
            },
            'en': {
                'morning': "🌷 April - Spring in full force! Season of travel and walks!",
                'afternoon': "🕑 April offers: Moto accessories for travel! 🏍️",
                'evening': "🌙 April: {} travelers, {} road customers"
            },
            'special_days': {
                '04_01': {  # Hazil kuni
                    'uz': "🎭 1-aprel - Hazil kuni! Ammo bizning takliflarimiz haqiqiy! 😄",
                    'ru': "🎭 1 апреля - День смеха! Но наши предложения реальны! 😄",
                    'en': "🎭 April 1st - April Fools' Day! But our offers are real! 😄"
                }
            }
        }
    
    def get_may_2026_messages(self):
        """May 2026 - Bahor yakuni, yoz boshlanishi"""
        return {
            'uz': {
                'morning': "🌞 May - Bahor yakuni, yoz boshlanishi! Issiq kunlar kelmoqda!",
                'afternoon': "🕑 May chegirmalari: Yozgi moto kiyimlari va aksessuarlari! ☀️",
                'evening': "🌙 May oyi: {} ta yozgi tayyorgarlik, {} ta issiqqa tayyor mijoz"
            },
            'ru': {
                'morning': "🌞 Май - Конец весны, начало лета! Приближаются жаркие дни!",
                'afternoon': "🕑 Майские скидки: Летняя мото одежда и аксессуары! ☀️",
                'evening': "🌙 Май: {} летних подготовок, {} клиентов готовых к жаре"
            },
            'en': {
                'morning': "🌞 May - End of spring, beginning of summer! Hot days are coming!",
                'afternoon': "🕑 May discounts: Summer moto clothes and accessories! ☀️",
                'evening': "🌙 May: {} summer preparations, {} heat-ready customers"
            },
            'special_days': {
                '05_09': {  # G'alaba kuni
                    'uz': "🎖️ G'alaba kuni! Bobokalonimizga hurmat va minnatdorchilik!",
                    'ru': "🎖️ День Победы! Уважение и благодарность нашим предкам!",
                    'en': "🎖️ Victory Day! Respect and gratitude to our ancestors!"
                }
            }
        }
    
    def get_june_2026_messages(self):
        """Iyun 2026 - Yozning birinchi oyi"""
        return {
            'uz': {
                'morning': "🏖️ Iyun - Yozning birinchi oyi! Dam olish va sayohat vaqti!",
                'afternoon': "🕑 Iyun takliflari: Dengiz yo'llari uchun moto uskunalari! 🌊",
                'evening': "🌙 Iyun statistika: {} ta dengizchi, {} ta sayohatchi mijoz"
            },
            'ru': {
                'morning': "🏖️ Июнь - Первый месяц лета! Время отдыха и путешествий!",
                'afternoon': "🕑 Июньские предложения: Мото оборудование для морских путей! 🌊",
                'evening': "🌙 Июньская статистика: {} моряков, {} путешественников-клиентов"
            },
            'en': {
                'morning': "🏖️ June - First month of summer! Time for rest and travel!",
                'afternoon': "🕑 June offers: Moto equipment for sea routes! 🌊",
                'evening': "🌙 June statistics: {} sailors, {} traveler customers"
            },
            'special_days': {
                '06_01': {  # Bolalar kuni
                    'uz': "👶 Xalqaro bolalar kuni! Kelajagimiz - bolalarimiz! 🎈",
                    'ru': "👶 Международный день защиты детей! Наше будущее - наши дети! 🎈",
                    'en': "👶 International Children's Day! Our future - our children! 🎈"
                }
            }
        }
    
    def get_july_2026_messages(self):
        """Iyul 2026 - Yozning eng issiq oyi"""
        return {
            'uz': {
                'morning': "🔥 Iyul - Yozning eng issiq oyi! Sovutish tizimlari muhim!",
                'afternoon': "🕑 Iyul maxsus: Moto sovutish tizimlari va ventilyatorlar! ❄️",
                'evening': "🌙 Iyul oyi: {} ta sovutish tizimi, {} ta issiqqa chidamli mijoz"
            },
            'ru': {
                'morning': "🔥 Июль - Самый жаркий месяц лета! Системы охлаждения важны!",
                'afternoon': "🕑 Июль специально: Мото системы охлаждения и вентиляторы! ❄️",
                'evening': "🌙 Июль: {} систем охлаждения, {} термостойких клиентов"
            },
            'en': {
                'morning': "🔥 July - Hottest month of summer! Cooling systems are important!",
                'afternoon': "🕑 July special: Moto cooling systems and fans! ❄️",
                'evening': "🌙 July: {} cooling systems, {} heat-resistant customers"
            }
        }
    
    def get_august_2026_messages(self):
        """Avgust 2026 - Yoz yakuni, kuz boshlanishi"""
        return {
            'uz': {
                'morning': "🍂 Avgust - Yoz yakuni, kuz boshlanishi! Maktabga qaytish vaqti!",
                'afternoon': "🕑 Avgust takliflari: O'quv mavsumi uchun moto aksessuarlari! 📚",
                'evening': "🌙 Avgust oyi: {} ta talaba, {} ta o'qituvchi mijoz"
            },
            'ru': {
                'morning': "🍂 Август - Конец лета, начало осени! Время возвращения в школу!",
                'afternoon': "🕑 Августовские предложения: Мото аксессуары для учебного сезона! 📚",
                'evening': "🌙 Август: {} студентов, {} учителей-клиентов"
            },
            'en': {
                'morning': "🍂 August - End of summer, beginning of autumn! Time to return to school!",
                'afternoon': "🕑 August offers: Moto accessories for study season! 📚",
                'evening': "🌙 August: {} students, {} teacher customers"
            }
        }
    
    def get_september_2026_messages(self):
        """Sentabr 2026 - Kuz, maktab boshlanishi"""
        return {
            'uz': {
                'morning': "📚 Sentabr - Maktab boshlanishi! Yangi bilimlar, yangi imkoniyatlar!",
                'afternoon': "🕑 Sentabr chegirmalari: Talabalar uchun maxsus takliflar! 🎓",
                'evening': "🌙 Sentabr statistika: {} ta talaba buyurtmasi, {} ta o'qituvchi"
            },
            'ru': {
                'morning': "📚 Сентябрь - Начало школы! Новые знания, новые возможности!",
                'afternoon': "🕑 Сентябрьские скидки: Специальные предложения для студентов! 🎓",
                'evening': "🌙 Сентябрьская статистика: {} студенческих заказов, {} учителей"
            },
            'en': {
                'morning': "📚 September - School start! New knowledge, new opportunities!",
                'afternoon': "🕑 September discounts: Special offers for students! 🎓",
                'evening': "🌙 September statistics: {} student orders, {} teachers"
            },
            'special_days': {
                '09_01': {  # Bilim kuni
                    'uz': "📖 Bilim kuni! Yangi o'quv yili muborak! 🎒",
                    'ru': "📖 День знаний! С новым учебным годом! 🎒",
                    'en': "📖 Knowledge Day! Happy new school year! 🎒"
                }
            }
        }
    
    def get_october_2026_messages(self):
        """Oktabr 2026 - Kuz ranglari, sovuq boshlanishi"""
        return {
            'uz': {
                'morning': "🍁 Oktabr - Kuz ranglari! Sovuq havolar kelmoqda, tayyorlaning!",
                'afternoon': "🕑 Oktabr maxsus: Qish oldidan moto texnik ko'rik! 🔧",
                'evening': "🌙 Oktabr oyi: {} ta texnik ko'rik, {} ta qishga tayyor mijoz"
            },
            'ru': {
                'morning': "🍁 Октябрь - Осенние краски! Приближаются холодные дни, готовьтесь!",
                'afternoon': "🕑 Октябрь специально: Мото технический осмотр перед зимой! 🔧",
                'evening': "🌙 Октябрь: {} технических осмотров, {} клиентов готовых к зиме"
            },
            'en': {
                'morning': "🍁 October - Autumn colors! Cold days are coming, get ready!",
                'afternoon': "🕑 October special: Moto technical inspection before winter! 🔧",
                'evening': "🌙 October: {} technical inspections, {} winter-ready customers"
            }
        }
    
    def get_november_2026_messages(self):
        """Noyabr 2026 - Qish oldi, sovuq kunlar"""
        return {
            'uz': {
                'morning': "❄️ Noyabr - Qish eslatmalari! Issiqlik va himoya muhim!",
                'afternoon': "🕑 Noyabr takliflari: Qishgi moto kiyimlari va qo'lqoplari! 🧤",
                'evening': "🌙 Noyabr statistika: {} ta qishgi kiyim, {} ta sovuqqa tayyor mijoz"
            },
            'ru': {
                'morning': "❄️ Ноябрь - Зимние напоминания! Тепло и защита важны!",
                'afternoon': "🕑 Ноябрьские предложения: Зимняя мото одежда и перчатки! 🧤",
                'evening': "🌙 Ноябрьская статистика: {} зимней одежды, {} клиентов готовых к холоду"
            },
            'en': {
                'morning': "❄️ November - Winter reminders! Warmth and protection are important!",
                'afternoon': "🕑 November offers: Winter moto clothes and gloves! 🧤",
                'evening': "🌙 November statistics: {} winter clothes, {} cold-ready customers"
            }
        }
    
    def get_december_2026_messages(self):
        """Dekabr 2026 - Yil yakuni, yangi yil tayyorgarligi"""
        return {
            'uz': {
                'morning': "🎄 Dekabr 2026! Yil yakuni, yangi imkoniyatlar boshlanishi!",
                'afternoon': "🕑 Dekabr maxsus: Yangi yil sovg'alari va maxsus takliflar! 🎁",
                'evening': "🌙 2026 yil yakuni: {} ta buyurtma, {} ta mamnun mijoz"
            },
            'ru': {
                'morning': "🎄 Декабрь 2026! Конец года, начало новых возможностей!",
                'afternoon': "🕑 Декабрь специально: Новогодние подарки и специальные предложения! 🎁",
                'evening': "🌙 Конец 2026 года: {} заказов, {} довольных клиентов"
            },
            'en': {
                'morning': "🎄 December 2026! End of year, beginning of new opportunities!",
                'afternoon': "🕑 December special: New Year gifts and special offers! 🎁",
                'evening': "🌙 End of 2026: {} orders, {} satisfied customers"
            }
        }
    
    # ==================== MESSAGE SENDING ====================
    
    def send_message_to_user(self, user_id, message):
        """Bitta foydalanuvchiga xabar yuborish"""
        try:
            import requests
            
            # Statistics ni to'ldirish
            stats = self.get_daily_stats()
            if '{}' in message:
                message = message.format(stats['orders'], stats['users'])
            
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
                return True
            else:
                logger.error(f"❌ Message error user_id={user_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Message error user_id={user_id}: {e}")
            return False
    
    def get_daily_stats(self):
        """Kunlik statistika"""
        try:
            # Bugungi buyurtmalar soni
            today = datetime.now().strftime('%Y-%m-%d')
            orders = self.db.get_orders()
            today_orders = sum(1 for order in orders if str(order[3]).startswith(today))
            
            # Jami foydalanuvchilar
            total_users = len(self.db.get_all_users())
            
            return {'orders': today_orders, 'users': total_users}
        except:
            return {'orders': 15, 'users': 50}  # Default qiymatlar
    
    def send_broadcast_by_time(self, message_type):
        """Vaqt bo'yicha xabar yuborish"""
        try:
            # Joriy sana
            now = self.get_tashkent_time()
            year = now.year
            month = now.month
            day = now.day
            
            # Barcha foydalanuvchilarni olish
            users = self.db.get_all_users()
            
            # Tillar bo'yicha guruhlash
            users_by_lang = {'uz': [], 'ru': [], 'en': []}
            
            for user in users:
                user_id = user[0]
                # Faqat ro'yxatdan o'tgan foydalanuvchilar
                if len(user) > 5 and user[5]:  # registered = TRUE
                    lang = self.get_user_language(user_id)
                    users_by_lang[lang].append(user_id)
            
            logger.info(f"📤 Broadcasting {message_type}: UZ={len(users_by_lang['uz'])}, RU={len(users_by_lang['ru'])}, EN={len(users_by_lang['en'])}")
            
            # Har bir til guruhiga xabar yuborish
            for lang, user_ids in users_by_lang.items():
                message = self.get_message_for_date(message_type, year, month, day, lang)
                
                successful = 0
                for user_id in user_ids:
                    if self.send_message_to_user(user_id, message):
                        successful += 1
                    
                    # Rate limit uchun
                    if successful % 10 == 0:
                        time.sleep(0.3)
                
                logger.info(f"✅ {lang.upper()}: {successful}/{len(user_ids)} sent")
            
            # Log yozish
            tashkent_time = self.get_tashkent_time().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"✅ Broadcast completed at {tashkent_time} ({message_type})")
            
        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}")
    
    def send_morning_message(self):
        """Ertalabki xabar (8:00)"""
        current_time = self.get_tashkent_time().strftime('%H:%M')
        logger.info(f"🕗 {current_time} - Sending morning messages...")
        self.send_broadcast_by_time('morning')
    
    def send_afternoon_message(self):
        """Tushki xabar (14:00)"""
        current_time = self.get_tashkent_time().strftime('%H:%M')
        logger.info(f"🕑 {current_time} - Sending afternoon messages...")
        self.send_broadcast_by_time('afternoon')
    
    def send_evening_message(self):
        """Kechki xabar (20:00)"""
        current_time = self.get_tashkent_time().strftime('%H:%M')
        logger.info(f"🕗 {current_time} - Sending evening messages...")
        self.send_broadcast_by_time('evening')
    
    # ==================== SCHEDULING ====================
    
    def schedule_messages(self):
        """Xabarlarni vaqt jadvaliga qo'yish (Toshkent vaqti)"""
        # Toshkent vaqti bilan (GMT+5)
        schedule.every().day.at("08:00").do(self.send_morning_message)
        schedule.every().day.at("14:00").do(self.send_afternoon_message)
        schedule.every().day.at("20:00").do(self.send_evening_message)
        
        logger.info("📅 Yearly messenger schedule: 8:00, 14:00, 20:00 (Tashkent)")
        
        # Jadvalni tekshirish loop'i
        while self.running:
            schedule.run_pending()
            
            # Har 5 daqiqa joriy vaqtni tekshirish
            current_time = self.get_tashkent_time()
            if current_time.minute % 5 == 0:
                logger.debug(f"⏰ Tashkent: {current_time.strftime('%Y-%m-%d %H:%M')}")
            
            time.sleep(60)
    
    def start(self):
        """Messenger ni ishga tushirish"""
        self.running = True
        
        # Dastlabki holat
        tashkent_time = self.get_tashkent_time()
        year, month = self.get_current_month_year()
        
        logger.info(f"📍 Tashkent timezone: Asia/Tashkent")
        logger.info(f"📅 Current date: {year}-{month}-{tashkent_time.day}")
        logger.info(f"⏰ Current time: {tashkent_time.strftime('%H:%M:%S')}")
        logger.info(f"🗓️ Loaded messages: 2025-12 to 2026-12")
        
        # Jadvalni sozlash
        thread = threading.Thread(target=self.schedule_messages, daemon=True)
        thread.start()
        
        logger.info("✅ Yearly messenger started (2025-2026)")
        return thread
    
    def stop(self):
        """To'xtatish"""
        self.running = False
        logger.info("🛑 Yearly messenger stopped")

# Global instance
yearly_messenger = None           