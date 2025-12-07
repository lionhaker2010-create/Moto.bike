# database.py - YANGI VERSIYA (PERSISTENT)
import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
   # database.py - Database class __init__ metodida

    def __init__(self):
        # RENDER muhitida bo'lsak, /data ni ishlatamiz
        if 'RENDER' in os.environ:
            # RENDER uchun /data papkasi
            self.db_path = '/data/motobike.db'
            logger.info(f"📁 Render database: {self.db_path}")
        else:
            # Local development - joriy papka
            self.db_path = 'motobike.db'
            logger.info(f"📁 Local database: {self.db_path}")
        
        self.init_db()
    
    def _get_connection(self):
        """Connection olish - Render uchun optimallashtirilgan"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def auto_backup(self):
        """Backup funksiyasi - faqat RENDER'da"""
        try:
            # Faqat RENDER muhitida backup olish
            if 'RENDER' not in os.environ:
                return
                
            if os.path.exists(self.db_path):
                backup_dir = '/data/backups'
                os.makedirs(backup_dir, exist_ok=True)
                
                backup_file = f"{backup_dir}/motobike_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db"
                import shutil
                shutil.copy2(self.db_path, backup_file)
                logger.info(f"✅ Render backup yaratildi: {backup_file}")
        except Exception as e:
            logger.error(f"❌ Backup yaratishda xatolik: {e}")
    
    # ... qolgan metodlar o'zgarmaydi, faqat db_path o'zgaradi ...

    def init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Foydalanuvchilar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    phone TEXT,
                    location TEXT,
                    language TEXT DEFAULT 'uz',
                    registered BOOLEAN DEFAULT FALSE,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    blocked BOOLEAN DEFAULT FALSE
                )
            ''')  # Bu # emas, Python comment!
            
            # Mahsulotlar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    subcategory TEXT,
                    name TEXT,
                    price REAL,
                    description TEXT,
                    image TEXT,
                    available BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Buyurtmalar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    location TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # To'lovlar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    receipt_photo TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
        
        # ... qolgan kod
            
            # Jadval mavjudligini tekshirish va yangi ustun qo'shish
            try:
                cursor.execute("SELECT blocked FROM users LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE users ADD COLUMN blocked BOOLEAN DEFAULT FALSE")
                logger.info("blocked ustuni qo'shildi")
            
            # To'lovlar jadvali uchun receipt_photo ustunini tekshirish
            try:
                cursor.execute("SELECT receipt_photo FROM payments LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE payments ADD COLUMN receipt_photo TEXT")
                logger.info("receipt_photo ustuni qo'shildi")
            
            # Buyurtmalar jadvali uchun location ustunini tekshirish
            try:
                cursor.execute("SELECT location FROM orders LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE orders ADD COLUMN location TEXT")
                logger.info("location ustuni orders jadvaliga qo'shildi")
            
            conn.commit()
            logger.info("Ma'lumotlar bazasi muvaffaqiyatli yaratildi/yangilandi")
            
        except Exception as e:
            logger.error(f"Ma'lumotlar bazasini yaratishda xatolik: {e}")
        finally:
            conn.close()
    
    def add_user(self, user_id, first_name):
        """Yangi foydalanuvchi qo'shish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)',
                (user_id, first_name)
            )
            conn.commit()
            logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id}")
        except Exception as e:
            logger.error(f"Foydalanuvchi qo'shishda xatolik: {e}")
        finally:
            conn.close()
    
    def update_user(self, user_id, **kwargs):
        """Foydalanuvchi ma'lumotlarini yangilash"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for key, value in kwargs.items():
                cursor.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', (value, user_id))
            
            conn.commit()
            logger.info(f"Foydalanuvchi yangilandi: {user_id} - {kwargs}")
        except Exception as e:
            logger.error(f"Foydalanuvchini yangilashda xatolik: {e}")
        finally:
            conn.close()
    
    def get_user(self, user_id):
        """Foydalanuvchi ma'lumotlarini olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            return user
        except Exception as e:
            logger.error(f"Foydalanuvchini olishda xatolik: {e}")
            return None
        finally:
            conn.close()
    
    def is_registered(self, user_id):
        """Foydalanuvchi ro'yxatdan o'tganmi tekshirish"""
        user = self.get_user(user_id)
        return user and user[5]  # registered maydoni (5-o'rinda)
    
    def block_user(self, user_id):
        """Foydalanuvchini bloklash"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET blocked = TRUE WHERE user_id = ?', (user_id,))
            conn.commit()
            logger.info(f"Foydalanuvchi bloklandi: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Foydalanuvchini bloklashda xatolik: {e}")
            return False
        finally:
            conn.close()
    
    def unblock_user(self, user_id):
        """Foydalanuvchini blokdan ochish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET blocked = FALSE WHERE user_id = ?', (user_id,))
            conn.commit()
            logger.info(f"Foydalanuvchi blokdan ochildi: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Foydalanuvchini blokdan ochishda xatolik: {e}")
            return False
        finally:
            conn.close()
    
    def add_product(self, category, subcategory, name, price, description, image=None):
        """Yangi mahsulot qo'shish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (category, subcategory, name, price, description, image)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, subcategory, name, price, description, image))
            conn.commit()
            logger.info(f"Yangi mahsulot qo'shildi: {name}")
            return True
        except Exception as e:
            logger.error(f"Mahsulot qo'shishda xatolik: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_users(self):
        """Barcha foydalanuvchilarni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY registration_date DESC')
            users = cursor.fetchall()
            return users
        except Exception as e:
            logger.error(f"Foydalanuvchilarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()
    
    def get_orders(self):
        """Buyurtmalarni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.id, u.first_name, p.name, o.order_date, o.status
                FROM orders o 
                LEFT JOIN users u ON o.user_id = u.user_id 
                LEFT JOIN products p ON o.product_id = p.id 
                ORDER BY o.order_date DESC
            ''')
            orders = cursor.fetchall()
            return orders
        except Exception as e:
            logger.error(f"Buyurtmalarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()
            
    def get_products_by_category(self, category, subcategory=None):
        """Kategoriya bo'yicha mahsulotlarni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if subcategory:
                cursor.execute('''
                    SELECT id, category, subcategory, name, price, description, image, available
                    FROM products 
                    WHERE category = ? AND subcategory = ? AND available = TRUE
                    ORDER BY id DESC
                ''', (category, subcategory))
            else:
                cursor.execute('''
                    SELECT id, category, subcategory, name, price, description, image, available
                    FROM products 
                    WHERE category = ? AND available = TRUE
                    ORDER BY id DESC
                ''', (category,))
            
            products = cursor.fetchall()
            return products
        except Exception as e:
            logger.error(f"Mahsulotlarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()

    def get_product_by_id(self, product_id):
        """ID bo'yicha mahsulotni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            product = cursor.fetchone()
            return product
        except Exception as e:
            logger.error(f"Mahsulotni olishda xatolik: {e}")
            return None
        finally:
            conn.close()

    def debug_products(self):
        """Mahsulotlarni tekshirish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, image FROM products')
            products = cursor.fetchall()
            
            print("=== MAHSULOTLAR DEBUG ===")
            for product in products:
                print(f"ID: {product[0]}, Name: {product[1]}, Image: {product[2]}")
            
            return products
        except Exception as e:
            print(f"Debug xatosi: {e}")
        finally:
            conn.close()
            
    def get_all_products(self):
        """Barcha mahsulotlarni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, category, subcategory, name, price, description, image, available
                FROM products 
                ORDER BY id DESC
            ''')
            products = cursor.fetchall()
            return products
        except Exception as e:
            logger.error(f"Barcha mahsulotlarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()

    def delete_product(self, product_id):
        """Mahsulotni o'chirish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            logger.info(f"Mahsulot o'chirildi: {product_id}")
            return True
        except Exception as e:
            logger.error(f"Mahsulotni o'chirishda xatolik: {e}")
            return False
        finally:
            conn.close()

    def get_products_by_category_only(self, category):
        """Faqat kategoriya bo'yicha mahsulotlarni olish (subcategory siz)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, category, subcategory, name, price, description, image, available
                FROM products 
                WHERE category = ? AND available = TRUE
                ORDER BY id DESC
            ''', (category,))
            products = cursor.fetchall()
            return products
        except Exception as e:
            logger.error(f"Kategoriya bo'yicha mahsulotlarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()
            
    # ============ YANGI FUNKSIYALAR ============

    def add_order(self, user_id, product_id, quantity=1, status='pending', location=None):
        """Yangi buyurtma qo'shish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (user_id, product_id, quantity, status, location)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, product_id, quantity, status, location))
            conn.commit()
            order_id = cursor.lastrowid
            logger.info(f"Yangi buyurtma qo'shildi: user_id={user_id}, product_id={product_id}, order_id={order_id}, location={location}")
            return order_id
        except Exception as e:
            logger.error(f"Buyurtma qo'shishda xatolik: {e}")
            return None
        finally:
            conn.close()

    # database.py faylida add_payment funksiyasiga debug qo'shing
    def add_payment(self, user_id, amount, status='pending', receipt_photo=None):
        """Yangi to'lov qo'shish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payments (user_id, amount, status, receipt_photo)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount, status, receipt_photo))
            conn.commit()
            payment_id = cursor.lastrowid
            logger.info(f"Yangi to'lov qo'shildi: user_id={user_id}, amount={amount}, payment_id={payment_id}, receipt_photo={receipt_photo}")
            return payment_id
        except Exception as e:
            logger.error(f"To'lov qo'shishda xatolik: {e}")
            return None
        finally:
            conn.close()
            
    def update_order_status(self, order_id, status):
        """Buyurtma statusini yangilash"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
            conn.commit()
            logger.info(f"Buyurtma statusi yangilandi: order_id={order_id}, status={status}")
            return True
        except Exception as e:
            logger.error(f"Buyurtma statusini yangilashda xatolik: {e}")
            return False
        finally:
            conn.close()

    def update_payment_status(self, payment_id, status):
        """To'lov statusini yangilash"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE payments SET status = ? WHERE id = ?', (status, payment_id))
            conn.commit()
            logger.info(f"To'lov statusi yangilandi: payment_id={payment_id}, status={status}")
            return True
        except Exception as e:
            logger.error(f"To'lov statusini yangilashda xatolik: {e}")
            return False
        finally:
            conn.close()

    def get_pending_orders(self):
        """Kutayotgan buyurtmalarni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.id, u.first_name, u.phone, p.name, o.quantity, o.order_date, o.status
                FROM orders o 
                LEFT JOIN users u ON o.user_id = u.user_id 
                LEFT JOIN products p ON o.product_id = p.id 
                WHERE o.status = 'pending'
                ORDER BY o.order_date DESC
            ''')
            orders = cursor.fetchall()
            return orders
        except Exception as e:
            logger.error(f"Kutayotgan buyurtmalarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()

    def get_pending_payments(self):
        """Kutayotgan to'lovlarni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, u.first_name, u.phone, p.amount, p.payment_date, p.status, p.receipt_photo
                FROM payments p 
                LEFT JOIN users u ON p.user_id = u.user_id 
                WHERE p.status = 'pending'
                ORDER BY p.payment_date DESC
            ''')
            payments = cursor.fetchall()
            return payments
        except Exception as e:
            logger.error(f"Kutayotgan to'lovlarni olishda xatolik: {e}")
            return []
        finally:
            conn.close()

    def get_payment_by_id(self, payment_id):
        """ID bo'yicha to'lovni olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
            payment = cursor.fetchone()
            
            # Debug uchun
            if payment:
                logger.info(f"To'lov topildi: ID={payment[0]}, User_ID={payment[1]}, Amount={payment[2]}")
            else:
                logger.warning(f"To'lov topilmadi: ID={payment_id}")
                
            return payment
        except Exception as e:
            logger.error(f"To'lovni olishda xatolik: {e}")
            return None
        finally:
            conn.close()

    def get_order_by_id(self, order_id):
        """ID bo'yicha buyurtmani olish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.*, u.first_name, u.phone, p.name, p.price 
                FROM orders o 
                LEFT JOIN users u ON o.user_id = u.user_id 
                LEFT JOIN products p ON o.product_id = p.id 
                WHERE o.id = ?
            ''', (order_id,))
            order = cursor.fetchone()
            return order
        except Exception as e:
            logger.error(f"Buyurtmani olishda xatolik: {e}")
            return None
        finally:
            conn.close()
            
            
    # database.py fayliga yangi funksiya:
    def clean_unregistered_users(self, days_old=1):
        """1 kundan ortiq ro'yxatdan o'tmagan foydalanuvchilarni o'chirish"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 1 kun oldin ro'yxatdan o'tmagan foydalanuvchilarni o'chirish
            cursor.execute('''
                DELETE FROM users 
                WHERE registered = FALSE 
                AND registration_date < datetime('now', '-? days')
            ''', (days_old,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"🧹 {deleted_count} ta ro'yxatdan o'tmagan foydalanuvchi o'chirildi")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Ro'yxatdan o'tmagan foydalanuvchilarni tozalashda xatolik: {e}")
            return 0
        finally:
            conn.close()

    # main.py ga qo'shing:
    def clean_unregistered_users_job():
        """Har kuni ro'yxatdan o'tmagan foydalanuvchilarni tozalash"""
        from database import db
        while True:
            try:
                deleted = db.clean_unregistered_users(1)  # 1 kun
                logger.info(f"✅ {deleted} ta ro'yxatdan o'tmagan foydalanuvchi tozalandi")
                time.sleep(86400)  # 24 soat
            except Exception as e:
                logger.error(f"❌ Tozalashda xatolik: {e}")
                time.sleep(3600)  # 1 soat        
                

# Global ma'lumotlar bazasi obyekti
db = Database()