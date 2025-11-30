import asyncio
from datetime import datetime
import asyncio
from datetime import datetime
import os
from telegram import InputMediaPhoto
import asyncio
from datetime import datetime
import asyncio
from datetime import datetime
import os
from telegram import InputMediaPhoto
import logging
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from database import db
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

# .env faylini yuklash
load_dotenv()

# Log qilishni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation holatlari
LANGUAGE, NAME, PHONE, LOCATION, MAIN_MENU, PRODUCT_SELECTED, PAYMENT_CONFIRMATION, WAITING_LOCATION = range(8)

# Til sozlamalari
TEXTS = {
    'uz': {
        'welcome': "👋 Assalomu Aleykum! Moto va Scooter Botiga Xush Kelibsiz!\n\nSiz bu botda Moto va Scooterlar uchun ehtiyot qism va kiyimlarni topshingiz mumkin. 🏍️\nArenda Electric Scooterlar ham mavjud! ⚡",
        'welcome_back': "👋 Xush kelibsiz! {name}",
        'choose_language': "🌐 Kerakli tilni tanlang:",
        'enter_name': "✍️ Iltimos, ismingizni kiriting:",
        'enter_phone': "📞 Telefon raqamingizni kiriting:",
        'share_location': "📍 Joylashuvingizni yuboring:",
        'checking_data': "🔍 Tekshirilmoqda...",
        'registration_success': "✅ Ro'yxatdan o'tish ma'lumotlaringiz tasdiqlandi!",
        'main_menu': "🏠 Asosiy menyu:",
        'support': "📞 Qo'llab-quvvatlash",
        'change_language': "🌐 Tilni o'zgartirish",
        'back': "⬅️ Orqaga",
        'language_changed': "✅ Til muvaffaqiyatli o'zgartirildi!"
    },
    'ru': {
        'welcome': "👋 Здравствуйте! Добро пожаловать в бот Moto и Scooter!\n\nЗдесь вы можете найти запчасти и одежду для мотоциклов и скутеров. 🏍️\nТакже доступны арендные электрические скутеры! ⚡",
        'welcome_back': "👋 С возвращением! {name}",
        'choose_language': "🌐 Выберите нужный язык:",
        'enter_name': "✍️ Пожалуйста, введите ваше имя:",
        'enter_phone': "📞 Введите ваш номер телефона:",
        'share_location': "📍 Отправьте ваше местоположение:",
        'checking_data': "🔍 Проверяется...",
        'registration_success': "✅ Ваши регистрационные данные подтверждены!",
        'main_menu': "🏠 Главное меню:",
        'support': "📞 Поддержка",
        'change_language': "🌐 Изменить язык",
        'back': "⬅️ Назад",
        'language_changed': "✅ Язык успешно изменен!"
    },
    'en': {
        'welcome': "👋 Hello! Welcome to Moto and Scooter Bot!\n\nHere you can find parts and clothing for motorcycles and scooters. 🏍️\nRental electric scooters are also available! ⚡",
        'welcome_back': "👋 Welcome back! {name}",
        'choose_language': "🌐 Choose your preferred language:",
        'enter_name': "✍️ Please enter your name:",
        'enter_phone': "📞 Enter your phone number:",
        'share_location': "📍 Share your location:",
        'checking_data': "🔍 Checking...",
        'registration_success': "✅ Your registration data has been confirmed!",
        'main_menu': "🏠 Main menu:",
        'support': "📞 Support",
        'change_language': "🌐 Change language",
        'back': "⬅️ Back",
        'language_changed': "✅ Language successfully changed!"
    }
}

def get_text(user_id, key, **kwargs):
    """Foydalanuvchi tiliga mos matnni qaytarish"""
    user = db.get_user(user_id)
    language = user[4] if user else 'uz'  # language maydoni
    text = TEXTS[language].get(key, key)
    return text.format(**kwargs) if kwargs else text

# Tugmalar
def get_language_keyboard():
    return ReplyKeyboardMarkup([
        ["🇺🇿 O'zbek", "🇷🇺 Русский", "🇺🇸 English"]
    ], resize_keyboard=True)

def get_phone_keyboard():
    return ReplyKeyboardMarkup([
        [{"text": "📞 Telefon raqamni yuborish", "request_contact": True}],
        ["⬅️ Orqaga"]
    ], resize_keyboard=True)

def get_location_keyboard():
    return ReplyKeyboardMarkup([
        [{"text": "📍 Joylashuvni yuborish", "request_location": True}],
        ["⬅️ Orqaga"]
    ], resize_keyboard=True)

def get_main_menu_keyboard(user_id):
    return ReplyKeyboardMarkup([
        ["🏍️ MotoBike", "🛵 Scooter", "⚡ Electric Scooter Arenda"],
        [get_text(user_id, 'support'), get_text(user_id, 'change_language')]
    ], resize_keyboard=True)

def get_motobike_keyboard(user_id):
    return ReplyKeyboardMarkup([
        ["🛡️ Shlemlar", "👕 Moto Kiyimlar", "👞 Oyoq kiyimlari"],
        ["🦵 Oyoq Himoya", "🧤 Qo'lqoplar", "🎭 Yuz himoya"],
        ["🔧 MOTO EHTIYOT QISMLAR", get_text(user_id, 'back')]
    ], resize_keyboard=True)

def get_parts_keyboard(user_id):
    return ReplyKeyboardMarkup([
        ["⚙️ Sep", "🛞 Disca", "🦋 Parushka"],
        ["🛑 Tormoz Ruchkasi", "💡 Old Chiroq", "🔴 Orqa Chiroq"],
        ["🪑 O'tirgichlar", "🔇 Glushitel", "🎛️ Gaz Trosi"],
        ["🔄 Sep Ruchkasi", "⛽ Benzin baki", "🔥 Svechalar"],
        ["⚡ Babinalar", "📦 Skores Karobka", "🔄 Karburator"],
        ["🛞 Apornik Disc", "🛑 Klotkalar", "🎨 Tunning Qismlari"],
        ["📦 Boshqa Qismlar", get_text(user_id, 'back')]
    ], resize_keyboard=True)

def get_scooter_keyboard(user_id):
    return ReplyKeyboardMarkup([
        ["⛽ Tank", "🚀 H Max", "⭐ Stell Max"],
        ["⚔️ Samuray", "🐅 Tiger", "🔧 Barcha Qismlar"],
        [get_text(user_id, 'back')]
    ], resize_keyboard=True)

def get_all_parts_keyboard(user_id):
    """Barcha scooter qismlari uchun umumiy menyu"""
    return ReplyKeyboardMarkup([
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

# Start komandasi - BLOKLASH TEKSHIRISHI QO'SHILDI
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # 1. Avval "labbey" deb javob beramiz
    await update.message.reply_text("labbey")
    
    # 2. Keyin admin tekshirish
    try:
        from admin import is_admin
        if is_admin(user_id):
            from admin import admin_start
            return await admin_start(update, context)
    except Exception as e:
        logger.error(f"Admin tekshirishda xatolik: {e}")
    
    # 3. Foydalanuvchi bloklanganligini tekshirish
    user_data = db.get_user(user_id)
    if user_data and len(user_data) >= 8 and user_data[7]:  # blocked maydoni
        await update.message.reply_text(
            "❌ **Siz bloklangansiz!**\n\n"
            "Botdan foydalanish huquqingiz cheklangan.\n"
            "Admin bilan bog'laning: @Operator_Kino_1985\n"
            "Yoki telefon: +998(98)8882505",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # ... qolgan kod o'zgarmaydi
    
    # Oddiy foydalanuvchi uchun ro'yxatdan o'tish jarayoni
    db.add_user(user_id, user.first_name)
    
    # Agar ro'yxatdan o'tgan bo'lsa, to'g'ridan-to'g'ri asosiy menyuga o'tkazish
    if db.is_registered(user_id):
        user_data = db.get_user(user_id)
        welcome_text = get_text(user_id, 'welcome_back', name=user_data[1])
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(user_id)
        )
        return MAIN_MENU
    else:
        # Ro'yxatdan o'tmagan bo'lsa, tilni tanlash bosqichi
        await update.message.reply_text(
            get_text(user_id, 'welcome'),
            reply_markup=get_language_keyboard()
        )
        return LANGUAGE

# Tilni tanlash - YANGILANDI
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if "O'zbek" in text:
        language = 'uz'
    elif "Русский" in text:
        language = 'ru'
    elif "English" in text:
        language = 'en'
    else:
        await update.message.reply_text(get_text(user_id, 'choose_language'))
        return LANGUAGE
    
    # Agar ro'yxatdan o'tgan bo'lsa, faqat tilni o'zgartirish
    if db.is_registered(user_id):
        db.update_user(user_id, language=language)
        await update.message.reply_text(
            get_text(user_id, 'language_changed'),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        return MAIN_MENU
    else:
        # Ro'yxatdan o'tmagan bo'lsa, ro'yxatdan o'tish jarayonini davom ettirish
        db.update_user(user_id, language=language)
        await update.message.reply_text(
            get_text(user_id, 'enter_name'),
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME

# Ism qabul qilish
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    user_id = update.effective_user.id
    
    db.update_user(user_id, first_name=name)
    await update.message.reply_text(
        get_text(user_id, 'enter_phone'),
        reply_markup=get_phone_keyboard()
    )
    return PHONE

# Telefon raqam qabul qilish
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
    
    db.update_user(user_id, phone=phone)
    await update.message.reply_text(
        get_text(user_id, 'share_location'),
        reply_markup=get_location_keyboard()
    )
    return LOCATION

# Joylashuv qabul qilish
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.message.location:
        location = f"{update.message.location.latitude}, {update.message.location.longitude}"
    else:
        location = update.message.text
    
    db.update_user(user_id, location=location, registered=True)
    
    # Tekshirish animatsiyasi
    checking_msg = await update.message.reply_text(get_text(user_id, 'checking_data'))
    for i in range(3):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=checking_msg.message_id,
            text=get_text(user_id, 'checking_data') + "." * (i + 1)
        )
        await asyncio.sleep(1)
    
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=checking_msg.message_id)
    await update.message.reply_text(
        get_text(user_id, 'registration_success'),
        reply_markup=get_main_menu_keyboard(user_id)
    )
    return MAIN_MENU

# Asosiy menyu
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if "MotoBike" in text:
        await update.message.reply_text(
            "🏍️ MotoBike bo'limi:",
            reply_markup=get_motobike_keyboard(user_id)
        )
    elif "Scooter" in text:
        await update.message.reply_text(
            "🛵 Scooter modellarini tanlang:",
            reply_markup=get_scooter_keyboard(user_id)
        )
    elif "Electric Scooter" in text:
        await update.message.reply_text(
            "⚡ Electric Scooter Arenda:\n\nMonster\nDrongo\nArenda\nVikup",
            reply_markup=get_main_menu_keyboard(user_id)
        )
    elif get_text(user_id, 'support') in text:
        await update.message.reply_text(
            "📞 **Qo'llab-quvvatlash:** @Operator_Kino_1985\n"
            "☎️ **Telefon:** +998(98)8882505\n\n"
            "🕒 **Ish vaqti:** 09:00 - 18:00\n"
            "💬 **Savollar bo'lsa, murojaat qiling!**",
            reply_markup=get_main_menu_keyboard(user_id)
        )
    elif get_text(user_id, 'change_language') in text:
        await update.message.reply_text(
            get_text(user_id, 'choose_language'),
            reply_markup=get_language_keyboard()
        )
        return LANGUAGE
    
    return MAIN_MENU

# Mahsulotlarni ko'rsatish uchun funksiyalar
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE, category, subcategory=None):
    """Mahsulotlarni ko'rsatish - BIRTA XABARDA 4 TA SURAT"""
    user_id = update.effective_user.id
    products = db.get_products_by_category(category, subcategory)
    
    if not products:
        await update.message.reply_text(
            "😔 Hozircha bu bo'limda mahsulotlar mavjud emas.\n\n"
            "Tez orada yangi mahsulotlar qo'shiladi!",
            reply_markup=get_motobike_keyboard(user_id) if "MotoBike" in category else get_scooter_keyboard(user_id)
        )
        return MAIN_MENU
    
    # Sahifalash
    page = context.user_data.get('products_page', 0)
    total_pages = len(products)  # Har bir mahsulot uchun alohida sahifa
    
    # Sahifa raqamini tekshirish
    if page >= total_pages:
        page = total_pages - 1
    if page < 0:
        page = 0
    
    current_product = products[page] if page < len(products) else None
    
    if current_product:
        product_id, prod_category, prod_subcategory, name, price, description, image, available = current_product
        
        # Rasmlarni o'qish
        photos = []
        if image and image != "[]" and image != "None" and image != "''" and image != '""':
            try:
                # String ni list ga aylantiramiz
                if isinstance(image, str):
                    photos = eval(image)
                else:
                    photos = image
            except Exception as e:
                logger.error(f"Rasmlarni o'qishda xatolik: {e}, image: {image}")
                photos = []
        
        # Matnni tozalash
        name_clean = name.replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')
        description_clean = description.replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')
        
        # Narxni formatlash
        price_formatted = f"{price:,.0f} so'm"
        
        message = (
            f"🏷️ **{name_clean}**\n\n"
            f"💰 **Narxi:** {price_formatted}\n"
            f"📝 **Tavsif:** {description_clean}\n\n"
            f"📞 **Buyurtma berish:** @Operator_Kino_1985\n"
            f"☎️ **Telefon:** +998(98)8882505\n\n"
            f"📄 Sahifa {page + 1}/{total_pages}"
        )
        
        # Agar rasmlar bo'lsa, BIRINCHI 4 TA RASMNI BIRGA YUBORAMIZ
        if photos:
            try:
                # Birinchi rasmni asosiy rasm qilamiz
                main_photo = photos[0]
                
                # Qolgan rasmlarni media guruhga qo'shamiz (maksimum 3 ta)
                media_group = []
                
                # Asosiy rasmni qo'shamiz
                media_group.append(InputMediaPhoto(media=main_photo, caption=message))
                
                # Qolgan rasmlarni qo'shamiz (2, 3, 4-rasmlar)
                for i, photo_id in enumerate(photos[1:4], 2):  # Faqat 2, 3, 4-rasmlarni olamiz
                    media_group.append(InputMediaPhoto(media=photo_id))
                
                # Media guruhni yuboramiz
                await update.message.reply_media_group(media=media_group)
                
                # Agar 4 tadan ko'p rasm bo'lsa, qolganlarini keyingi xabarda
                if len(photos) > 4:
                    remaining_photos = photos[4:]
                    remaining_media = []
                    
                    for i, photo_id in enumerate(remaining_photos, 5):
                        remaining_media.append(InputMediaPhoto(media=photo_id))
                    
                    await update.message.reply_media_group(media=remaining_media)
                    
            except Exception as e:
                logger.error(f"Rasm yuborishda xatolik: {e}")
                # Rasm yuborishda xatolik bo'lsa, faqat tekst yuboramiz
                await update.message.reply_text(
                    f"📸 {message}\n\n⚠️ Rasm yuklashda xatolik"
                )
        else:
            # Rasmlar yo'q bo'lsa
            await update.message.reply_text(
                f"📦 {message}\n\n🖼️ Rasmlar mavjud emas"
            )
    
    # Sahifalash tugmalari
    pagination_keyboard = []
    
    # Oldingi sahifa tugmasi
    if page > 0:
        pagination_keyboard.append(["⬅️ Oldingi sahifa"])
    
    # Keyingi sahifa tugmasi  
    if page < total_pages - 1:
        pagination_keyboard.append(["Keyingi sahifa ➡️"])
    
    # Orqaga tugmasi
    pagination_keyboard.append(["🔙 Orqaga"])
    
    await update.message.reply_text(
        f"📄 Sahifa {page + 1}/{total_pages} - {len(products)} ta mahsulot",
        reply_markup=ReplyKeyboardMarkup(pagination_keyboard, resize_keyboard=True)
    )
    
    context.user_data['products_page'] = page
    context.user_data['total_products_pages'] = total_pages
    context.user_data['current_category'] = category
    context.user_data['current_subcategory'] = subcategory
    
    # BUYURTMA TUGMALARI - return MAIN_MENU dan OLDIN
    order_keyboard = []
    order_keyboard.append(["💰 To'lov qilish", "📦 Buyurtma berish"])
    order_keyboard.append(["🔙 Orqaga"])
    
    await update.message.reply_text(
        f"🛒 **Mahsulot tanlandi!**\n\n"
        f"🏷️ {name_clean}\n"
        f"💰 {price_formatted}\n\n"
        f"Quyidagi amallardan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(order_keyboard, resize_keyboard=True)
    )
    
    # Tanlangan mahsulotni saqlaymiz
    context.user_data['selected_product'] = current_product
    context.user_data['selected_product_id'] = product_id
    
    return PRODUCT_SELECTED  # MAIN_MENU emas, PRODUCT_SELECTED ga qaytamiz

# MotoBike menyusi - YANGILANDI
async def motobike_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            get_text(user_id, 'main_menu'),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        return MAIN_MENU
    
    elif "MOTO EHTIYOT QISMLAR" in text:
        await update.message.reply_text(
            "🔧 MOTO EHTIYOT QISMLARI:",
            reply_markup=get_parts_keyboard(user_id)
        )
        return MAIN_MENU
    
    elif text in ["🛡️ Shlemlar", "👕 Moto Kiyimlar", "👞 Oyoq kiyimlari", 
                  "🦵 Oyoq Himoya", "🧤 Qo'lqoplar", "🎭 Yuz himoya"]:
        # Sahifalashni boshlash
        context.user_data['products_page'] = 0
        await show_products(update, context, "🏍️ MotoBike", text)
        return MAIN_MENU
    
    elif text in ["⬅️ Oldingi sahifa", "Keyingi sahifa ➡️"]:
        # Sahifalash
        page = context.user_data.get('products_page', 0)
        total_pages = context.user_data.get('total_products_pages', 1)
        
        if text == "⬅️ Oldingi sahifa" and page > 0:
            context.user_data['products_page'] = page - 1
        elif text == "Keyingi sahifa ➡️" and page < total_pages - 1:
            context.user_data['products_page'] = page + 1
        else:
            # Sahifa chegarasidan chiqib ketish
            await update.message.reply_text("ℹ️ Boshqa sahifa mavjud emas")
            return MAIN_MENU
        
        category = context.user_data.get('current_category')
        subcategory = context.user_data.get('current_subcategory')
        await show_products(update, context, category, subcategory)
        return MAIN_MENU
    
    else:
        await update.message.reply_text(
            f"✅ Siz tanladingiz: {text}\n\nTez orada bu bo'lim ishga tushadi!",
            reply_markup=get_motobike_keyboard(user_id)
        )
    
    return MAIN_MENU

# Ehtiyot qismlar menyusi - YANGILANDI
async def parts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            "🏍️ MotoBike bo'limi:",
            reply_markup=get_motobike_keyboard(user_id)
        )
        return MAIN_MENU
    
    # qolgan kod o'zgarmaydi...
    
    elif text in ["⬅️ Oldingi sahifa", "Keyingi sahifa ➡️"]:
        # Sahifalash
        page = context.user_data.get('products_page', 0)
        total_pages = context.user_data.get('total_products_pages', 1)
        
        if text == "⬅️ Oldingi sahifa" and page > 0:
            context.user_data['products_page'] = page - 1
        elif text == "Keyingi sahifa ➡️" and page < total_pages - 1:
            context.user_data['products_page'] = page + 1
        
        category = context.user_data.get('current_category')
        subcategory = context.user_data.get('current_subcategory')
        await show_products(update, context, category, subcategory)
        return MAIN_MENU
    
    else:
        # Ehtiyot qismlarni ko'rsatish
        await show_products(update, context, "🏍️ MotoBike", "🔧 MOTO EHTIYOT QISMLAR")
    
    return MAIN_MENU

# Scooter menyusi - YANGILANDI
async def scooter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if get_text(user_id, 'back') in text:
        await update.message.reply_text(
            get_text(user_id, 'main_menu'),
            reply_markup=get_main_menu_keyboard(user_id)
        )
        return MAIN_MENU
    
    elif text == "🔧 Barcha Qismlar":
        await update.message.reply_text(
            "🔧 **Barcha Scooter Qismlari**\n\nAdmin tomonidan qo'shiladi",
            reply_markup=get_scooter_keyboard(user_id)
        )
        return MAIN_MENU
    
    elif text in ["⬅️ Oldingi sahifa", "Keyingi sahifa ➡️"]:
        # Sahifalash
        page = context.user_data.get('products_page', 0)
        total_pages = context.user_data.get('total_products_pages', 1)
        
        if text == "⬅️ Oldingi sahifa" and page > 0:
            context.user_data['products_page'] = page - 1
        elif text == "Keyingi sahifa ➡️" and page < total_pages - 1:
            context.user_data['products_page'] = page + 1
        
        category = context.user_data.get('current_category')
        subcategory = context.user_data.get('current_subcategory')
        await show_products(update, context, category, subcategory)
        return MAIN_MENU
    
    else:
        # Scooter mahsulotlarini ko'rsatish
        await show_products(update, context, "🛵 Scooter", text)
    
    return MAIN_MENU

# Barcha qismlar menyusi
async def all_parts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if get_text(user_id, 'back') in text:
        await update.message.reply_text(
            "🛵 Scooter modellarini tanlang:",
            reply_markup=get_scooter_keyboard(user_id)
        )
        return MAIN_MENU
    
    return MAIN_MENU

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sahifalashni boshqarish"""
    user_id = update.effective_user.id
    text = update.message.text
    
    page = context.user_data.get('products_page', 0)
    total_pages = context.user_data.get('total_products_pages', 1)
    category = context.user_data.get('current_category')
    subcategory = context.user_data.get('current_subcategory')
    
    if text == "⬅️ Oldingi sahifa" and page > 0:
        context.user_data['products_page'] = page - 1
    elif text == "Keyingi sahifa ➡️" and page < total_pages - 1:
        context.user_data['products_page'] = page + 1
    else:
        await update.message.reply_text("ℹ️ Boshqa sahifa mavjud emas")
        return MAIN_MENU
    
    await show_products(update, context, category, subcategory)
    return MAIN_MENU

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Orqaga qaytish"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "🔙 Orqaga":
        # Kategoriyaga qarab turli menyularga qaytish
        category = context.user_data.get('current_category', '')
        
        if "MotoBike" in category:
            await update.message.reply_text(
                "🏍️ MotoBike bo'limi:",
                reply_markup=get_motobike_keyboard(user_id)
            )
        elif "Scooter" in category:
            await update.message.reply_text(
                "🛵 Scooter modellarini tanlang:",
                reply_markup=get_scooter_keyboard(user_id)
            )
        else:
            await update.message.reply_text(
                get_text(user_id, 'main_menu'),
                reply_markup=get_main_menu_keyboard(user_id)
            )
        return MAIN_MENU
    
    return MAIN_MENU  

# handle_back funksiyasidan KEYIN:

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulot tanlanganida"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "💰 To'lov qilish":
        await update.message.reply_text(
            "💳 **To'lov usulini tanlang:**\n\n"
            "1️⃣ **Click** - *9860 3501 4890 3205*\n"
            "2️⃣ **Payme** - *9860 3501 4890 3205*\n"
            "3️⃣ **Naqd pul** - *Yetkazib berishda*\n\n"
            "To'lov qilgach, chek rasmini yuboring:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return PAYMENT_CONFIRMATION
    
    elif text == "📦 Buyurtma berish":
        # Ma'lumotlarni tekshirish animatsiyasi
        checking_msg = await update.message.reply_text("🔍 Ma'lumotlar tekshirilmoqda")
        for i in range(3):
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=checking_msg.message_id,
                text="🔍 Ma'lumotlar tekshirilmoqda" + "." * (i + 1)
            )
            await asyncio.sleep(1)
        
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=checking_msg.message_id)
        
        await update.message.reply_text(
            "✅ **Ma'lumotlaringiz tasdiqlandi!**\n\n"
            "📍 **Iltimos, joylashuvingizni yuboring:**\n\n"
            "Yetkazib berish manzilini aniq belgilash uchun joylashuvingizni yuboring.",
            reply_markup=ReplyKeyboardMarkup([
                [{"text": "📍 Joylashuvni yuborish", "request_location": True}],
                ["🔙 Orqaga"]
            ], resize_keyboard=True)
        )
        return WAITING_LOCATION
    
    elif text == "🔙 Orqaga":
        # Oldingi menyuga qaytish
        category = context.user_data.get('current_category')
        await show_products(update, context, category)
        return MAIN_MENU
    
    return PRODUCT_SELECTED

async def payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov tasdiqlash"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            "🛒 **Mahsulot tanlandi!**\n\n"
            "Quyidagi amallardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup([
                ["💰 To'lov qilish", "📦 Buyurtma berish"],
                ["🔙 Orqaga"]
            ], resize_keyboard=True)
        )
        return PRODUCT_SELECTED
    
    # Rasm yuborilgan bo'lsa (chek rasmi)
    elif update.message.photo:
        # Chek rasmini saqlaymiz
        photo = update.message.photo[-1]
        context.user_data['payment_receipt'] = photo.file_id
        logger.info(f"To'lov cheki qabul qilindi: file_id={photo.file_id}")
        
        # Ma'lumotlarni tekshirish animatsiyasi
        checking_msg = await update.message.reply_text("🔍 To'lov tekshirilmoqda")
        for i in range(3):
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=checking_msg.message_id,
                text="🔍 To'lov tekshirilmoqda" + "." * (i + 1)
            )
            await asyncio.sleep(1)
        
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=checking_msg.message_id)
        
        await update.message.reply_text(
            "✅ **To'lov muvaffaqiyatli qabul qilindi!**\n\n"
            "📍 **Iltimos, joylashuvingizni yuboring:**\n\n"
            "Yetkazib berish manzilini aniq belgilash uchun joylashuvingizni yuboring.",
            reply_markup=ReplyKeyboardMarkup([
                [{"text": "📍 Joylashuvni yuborish", "request_location": True}],
                ["🔙 Orqaga"]
            ], resize_keyboard=True)
        )
        return WAITING_LOCATION
    
    else:
        await update.message.reply_text(
            "📸 **Iltimos, to'lov cheki rasmini yuboring yoki orqaga qayting:**",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return PAYMENT_CONFIRMATION

async def waiting_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Joylashuv kutish - FOYDALANUVCHIGA XABAR YUBORILMAYDI"""
    user_id = update.effective_user.id
    text = update.message.text if update.message.text else ""
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            "🛒 **Mahsulot tanlandi!**\n\n"
            "Quyidagi amallardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup([
                ["💰 To'lov qilish", "📦 Buyurtma berish"],
                ["🔙 Orqaga"]
            ], resize_keyboard=True)
        )
        return PRODUCT_SELECTED
    
    elif update.message.location:
        location = f"{update.message.location.latitude}, {update.message.location.longitude}"
        context.user_data['delivery_location'] = location
        
        # Buyurtma ma'lumotlarini olish
        product = context.user_data.get('selected_product')
        product_name = product[3] if product else "Noma'lum mahsulot"
        product_price = product[4] if product else 0
        
        # Adminlarga xabar yuborish
        await send_order_to_admin(update, context, user_id, product_name, product_price, location)
        
        # Foydalanuvchiga KUTISH xabari yuboramiz
        await update.message.reply_text(
            "⏳ **Buyurtmangiz qabul qilindi va admin tasdigini kutmoqda!**\n\n"
            "✅ **Buyurtma ma'lumotlari admin panelga yuborildi**\n"
            "👨‍💼 **Admin tez orada buyurtmangizni ko'rib chiqadi**\n"
            "📞 **Tasdiqlangan taqdirda siz bilan bog'lanamiz**\n\n"
            "🕒 **Ish vaqti:** 09:00 - 18:00\n"
            "👤 **Operator:** @Operator_Kino_1985\n"
            "☎️ **Telefon:** +998(98)8882505",
            reply_markup=get_main_menu_keyboard(user_id)
        )
        
        # User datani tozalash
        context.user_data.clear()
        return MAIN_MENU
    
    else:
        await update.message.reply_text(
            "📍 **Iltimos, joylashuvingizni yuboring:**\n\n"
            "Yetkazib berish manzilini aniq belgilash uchun joylashuvingizni yuboring.",
            reply_markup=ReplyKeyboardMarkup([
                [{"text": "📍 Joylashuvni yuborish", "request_location": True}],
                ["🔙 Orqaga"]
            ], resize_keyboard=True)
        )
        return WAITING_LOCATION
        
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugmalarni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = query.from_user.id
    
    # Admin tekshirish
    from admin import is_admin
    if not is_admin(user_id):
        await query.edit_message_text("❌ Siz admin emassiz!")
        return
    
    if callback_data.startswith('confirm_order_'):
        order_id = int(callback_data.replace('confirm_order_', ''))
        await confirm_order_callback(query, context, order_id)
    
    elif callback_data.startswith('reject_order_'):
        order_id = int(callback_data.replace('reject_order_', ''))
        await reject_order_callback(query, context, order_id)
    
    elif callback_data.startswith('confirm_payment_'):
        payment_id = int(callback_data.replace('confirm_payment_', ''))
        await confirm_payment_callback(query, context, payment_id)
    
    elif callback_data.startswith('reject_payment_'):
        payment_id = int(callback_data.replace('reject_payment_', ''))
        await reject_payment_callback(query, context, payment_id)
    
    elif callback_data.startswith('fake_payment_'):
        payment_id = int(callback_data.replace('fake_payment_', ''))
        await mark_fake_payment_callback(query, context, payment_id)
    
    elif callback_data.startswith('contact_'):
        contact_user_id = int(callback_data.replace('contact_', ''))
        await contact_customer_callback(query, context, contact_user_id)

async def confirm_order_callback(query, context, order_id):
    """Buyurtmani tasdiqlash (callback)"""
    success = db.update_order_status(order_id, 'completed')
    
    if success:
        # Buyurtma ma'lumotlarini olish
        order_info = db.get_order_by_id(order_id)
        if order_info:
            user_id = order_info[1]
            location = order_info[6] if len(order_info) > 6 else "Joylashuv ko'rsatilmagan"  # location maydoni
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 **BUYURTMANGIZ TASDIQLANDI!** 🎉\n\n"
                         f"✅ **Buyurtmangiz muvaffaqiyatli tasdiqlandi!**\n"
                         f"🚚 **Tez orada siz bilan etkazib berish xizmatchilarimiz bog'lanadi**\n"
                         f"📍 **Joylashuvingiz:** {location}\n"
                         f"📞 **Iltimos, telefoningiz doim aloqada bo'lsin**\n\n"
                         f"🕒 **Ish vaqti:** 09:00 - 18:00\n"
                         f"👤 **Operator:** @Operator_Kino_1985\n"
                         f"☎️ **Telefon:** +998(98)8882505"
                )
            except Exception as e:
                logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
        
        await query.edit_message_text(
            f"✅ **Buyurtma #{order_id} muvaffaqiyatli tasdiqlandi!**\n\n"
            f"📍 **Joylashuv:** {location}\n"
            f"Mijozga tasdiqlash haqida xabar yuborildi."
        )
    else:
        await query.edit_message_text(f"❌ **Buyurtma #{order_id} topilmadi!**")

async def confirm_payment_callback(query, context, payment_id):
    """To'lovni tasdiqlash (callback)"""
    success = db.update_payment_status(payment_id, 'completed')
    
    if success:
        # To'lov ma'lumotlarini olish
        payment_info = db.get_payment_by_id(payment_id)
        if payment_info:
            user_id = payment_info[1]
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 **TO'LOVINGIZ TASDIQLANDI!** 🎉\n\n"
                         "✅ **To'lov muvaffaqiyatli tasdiqlandi!**\n"
                         "🚚 **Tez orada siz bilan etkazib berish xizmatchilarimiz bog'lanadi**\n"
                         "📍 **Joylashuvingiz:** Berilgan manzil bo'yicha\n"
                         "📞 **Iltimos, telefoningiz doim aloqada bo'lsin**\n\n"
                         "🕒 **Ish vaqti:** 09:00 - 18:00\n"
                         "👤 **Operator:** @Operator_Kino_1985\n"
                         "☎️ **Telefon:** +998(98)8882505"
                )
            except Exception as e:
                logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
        
        await query.edit_message_text(
            f"✅ **To'lov #{payment_id} muvaffaqiyatli tasdiqlandi!**\n\n"
            f"Mijozga tasdiqlash haqida xabar yuborildi."
        )
    else:
        await query.edit_message_text(f"❌ **To'lov #{payment_id} topilmadi!**")

# Qolgan callback funksiyalarni ham shu tarzda yozing
async def reject_order_callback(query, context, order_id):
    """Buyurtmani rad etish"""
    success = db.update_order_status(order_id, 'rejected')
    # ... implement ...

async def reject_payment_callback(query, context, payment_id):
    """To'lovni rad etish"""
    success = db.update_payment_status(payment_id, 'rejected')
    # ... implement ...

async def mark_fake_payment_callback(query, context, payment_id):
    """Sohta chek deb belgilash"""
    success = db.update_payment_status(payment_id, 'fake')
    # ... implement ...

async def contact_customer_callback(query, context, user_id):
    """Mijoz bilan bog'lanish"""
    await query.edit_message_text(
        f"👤 **Mijoz bilan bog'lanish**\n\n"
        f"Foydalanuvchi ID: `{user_id}`\n\n"
        f"Endi ushbu foydalanuvchiga yubormoqchi bo'lgan xabaringizni yuboring:",
        parse_mode='Markdown'
    )
    # Context ga ma'lumot saqlash kerak         

def update_order_status(order_id, status):
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

def add_payment(user_id, amount, status='pending', receipt_photo=None):
    """Yangi to'lov qo'shish"""
    try:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, amount, status, receipt_photo)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, status, receipt_photo))
        conn.commit()
        logger.info(f"Yangi to'lov qo'shildi: user_id={user_id}, amount={amount}")
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"To'lov qo'shishda xatolik: {e}")
        return None
    finally:
        conn.close()

def update_payment_status(payment_id, status):
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

def get_pending_orders():
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
        
async def send_order_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, product_name, product_price, location):
    """Adminlarga buyurtma haqida xabar yuborish"""
    try:
        user_data = db.get_user(user_id)
        user_name = user_data[1] if user_data else "Noma'lum"
        user_phone = user_data[2] if user_data and len(user_data) > 2 else "Noma'lum"
        
        # Buyurtmani ma'lumotlar bazasiga qo'shamiz (joylashuv bilan)
        product_id = context.user_data.get('selected_product_id')
        order_id = db.add_order(user_id, product_id, 1, 'pending', location)  # Joylashuv qo'shildi
        
        # ... qolgan kod ...
        
        # Buyurtmani ma'lumotlar bazasiga qo'shamiz
        product_id = context.user_data.get('selected_product_id')
        order_id = db.add_order(user_id, product_id, 1, 'pending')
        
        # To'lov cheki bo'lsa, to'lovni ham qo'shamiz
        receipt_photo = context.user_data.get('payment_receipt')
        payment_id = None
        
        if receipt_photo:
            payment_id = db.add_payment(user_id, product_price, 'pending', receipt_photo)
            logger.info(f"To'lov qo'shildi: payment_id={payment_id}, receipt_photo={receipt_photo}")
        else:
            logger.info("To'lov cheki yo'q")
        
        order_message = (
            f"🆕 **YANGI BUYURTMA!**\n\n"
            f"👤 **Foydalanuvchi:** {user_name}\n"
            f"🆔 **ID:** {user_id}\n"
            f"📞 **Telefon:** {user_phone}\n"
            f"📦 **Mahsulot:** {product_name}\n"
            f"💰 **Narxi:** {product_price:,.0f} so'm\n"
            f"📍 **Joylashuv:** [Google Maps](https://maps.google.com/?q={location}) | [Yandex Maps](https://yandex.com/maps/?text={location})\n\n"
            f"🆔 **Buyurtma ID:** {order_id}\n"
        )
        
        # Agar to'lov bo'lsa, to'lov ID sini qo'shamiz
        if payment_id:
            order_message += f"💳 **To'lov ID:** {payment_id}\n"
        
        order_message += f"⏰ **Vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Admin ID sini olish
        admin_id = os.getenv('ADMIN_ID')
        if admin_id:
            logger.info(f"Adminga xabar yuborilmoqda: {admin_id}")
            
            # INLINE KEYBOARD yaratamiz
            keyboard = []
            
            if order_id:
                keyboard.append([
                    InlineKeyboardButton("✅ Buyurtmani Tasdiqlash", callback_data=f"confirm_order_{order_id}"),
                    InlineKeyboardButton("❌ Buyurtmani Rad Etish", callback_data=f"reject_order_{order_id}")
                ])
            
            if payment_id:
                keyboard.append([
                    InlineKeyboardButton("✅ To'lovni Tasdiqlash", callback_data=f"confirm_payment_{payment_id}"),
                    InlineKeyboardButton("❌ To'lovni Rad Etish", callback_data=f"reject_payment_{payment_id}")
                ])
            
            keyboard.append([
                InlineKeyboardButton("📞 Mijoz bilan Bog'lanish", callback_data=f"contact_{user_id}")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Buyurtma xabarini yuboramiz
            await context.bot.send_message(
                chat_id=admin_id,
                text=order_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Mahsulot rasmini yuboramiz
            product = context.user_data.get('selected_product')
            if product and len(product) > 6:
                product_image = product[6]  # image maydoni
                if product_image and product_image != "[]":
                    try:
                        photos = eval(product_image)
                        if photos:
                            await context.bot.send_photo(
                                chat_id=admin_id,
                                photo=photos[0],
                                caption="🖼️ Buyurtma qilingan mahsulot"
                            )
                    except Exception as e:
                        logger.error(f"Mahsulot rasmini yuborishda xatolik: {e}")
            
            # Agar to'lov cheki bo'lsa, uni ham yuboramiz
            if receipt_photo and payment_id:
                payment_message = (
                    f"💳 **YANGI TO'LOV!**\n\n"
                    f"👤 **Foydalanuvchi:** {user_name}\n"
                    f"💰 **Summa:** {product_price:,.0f} so'm\n"
                    f"🆔 **To'lov ID:** {payment_id}\n"
                    f"⏰ **Vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # To'lov cheki uchun ham inline keyboard yaratamiz
                payment_keyboard = [
                    [
                        InlineKeyboardButton("✅ To'lovni Tasdiqlash", callback_data=f"confirm_payment_{payment_id}"),
                        InlineKeyboardButton("❌ To'lovni Rad Etish", callback_data=f"reject_payment_{payment_id}")
                    ],
                    [
                        InlineKeyboardButton("⚠️ Sohta Chek Deb Belgilash", callback_data=f"fake_payment_{payment_id}")
                    ],
                    [
                        InlineKeyboardButton("📞 Mijoz bilan Bog'lanish", callback_data=f"contact_{user_id}")
                    ]
                ]
                
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=receipt_photo,
                    caption=payment_message,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(payment_keyboard)
                )
                logger.info(f"To'lov cheki adminga yuborildi: payment_id={payment_id}")
            else:
                logger.info("To'lov cheki yo'q, shuning uchun yuborilmadi")
                
            logger.info("Adminga xabar muvaffaqiyatli yuborildi")
        else:
            logger.error("ADMIN_ID topilmadi!")
                
    except Exception as e:
        logger.error(f"Adminlarga xabar yuborishda xatolik: {e}")       

def get_pending_payments():
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
    
# ==================== ASOSIY FUNKSIYA ====================

def main():
    """Asosiy bot funksiyasi"""
    # Bot tokenini olish
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return
    
    try:
        # Bot ilovasini yaratish
        application = Application.builder().token(TOKEN).build()
        
        # 1. Avval ADMIN handlerini qo'shamiz
        from admin import get_admin_handler
        application.add_handler(get_admin_handler())
        
        # 2. Callback query handler qo'shamiz
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # 3. Conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), get_phone)],
                LOCATION: [MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), get_location)],
                MAIN_MENU: [
                    MessageHandler(filters.Regex("^(🏍️ MotoBike|🛵 Scooter|⚡ Electric Scooter Arenda)$"), main_menu),
                    MessageHandler(filters.Regex("^(🛡️ Shlemlar|👕 Moto Kiyimlar|👞 Oyoq kiyimlari|🦵 Oyoq Himoya|🧤 Qo'lqoplar|🎭 Yuz himoya|🔧 MOTO EHTIYOT QISMLAR)$"), motobike_menu),
                    MessageHandler(filters.Regex("^(⚙️ Sep|🛞 Disca|🦋 Parushka|🛑 Tormoz Ruchkasi|💡 Old Chiroq|🔴 Orqa Chiroq|🪑 O'tirgichlar|🔇 Glushitel|🎛️ Gaz Trosi|🔄 Sep Ruchkasi|⛽ Benzin baki|🔥 Svechalar|⚡ Babinalar|📦 Skores Karobka|🔄 Karburator|🛞 Apornik Disc|🛑 Klotkalar|🎨 Tunning Qismlari|📦 Boshqa Qismlari)$"), parts_menu),
                    MessageHandler(filters.Regex("^(⛽ Tank|🚀 H Max|⭐ Stell Max|⚔️ Samuray|🐅 Tiger|🔧 Barcha Qismlari)$"), scooter_menu),
                    MessageHandler(filters.Regex("^(⬅️ Oldingi sahifa|Keyingi sahifa ➡️)$"), handle_pagination),
                    MessageHandler(filters.Regex("^(💰 To'lov qilish|📦 Buyurtma berish)$"), product_selected),
                    MessageHandler(filters.Regex("^(🔙 Orqaga)$"), handle_back),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)
                ],
                PRODUCT_SELECTED: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, product_selected)
                ],
                PAYMENT_CONFIRMATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, payment_confirmation),
                    MessageHandler(filters.PHOTO, payment_confirmation)
                ],
                WAITING_LOCATION: [
                    MessageHandler(filters.LOCATION, waiting_location),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, waiting_location)
                ],
            },
            fallbacks=[CommandHandler('start', start)],
            allow_reentry=True
        )
        
        application.add_handler(conv_handler)
        
        # Bot ishga tushganda xabar
        logger.info("🤖 Bot ishga tushdi va polling ni boshladi!")
        
        # Botni ishga tushirish (polling)
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Botda xatolik yuz berdi: {e}")
        # Xatolik yuz berganda qayta ishga tushish
        import time
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()