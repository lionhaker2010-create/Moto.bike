import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
from database import db

logger = logging.getLogger(__name__)

# Admin conversation holatlari - BARCHASINI BIR QATORGA YOZAMIZ
(
    ADMIN_MAIN, ADD_PRODUCT_CATEGORY, ADD_PRODUCT_SUBCATEGORY, ADD_PRODUCT_NAME, 
    ADD_PRODUCT_PRICE_TYPE, ADD_PRODUCT_PRICE, ADD_PRODUCT_DESC, ADD_PRODUCT_PHOTOS, 
    DELETE_PRODUCT_CATEGORY, DELETE_PRODUCT_SELECT, DELETE_PRODUCT_CONFIRM, 
    ORDER_MANAGEMENT, CONFIRM_ORDER, REJECT_ORDER, CONFIRM_PAYMENT, REJECT_PAYMENT, MARK_FAKE_PAYMENT
) = range(17)

# Admin tekshirish funksiyasi
def is_admin(user_id):
    admin_id = os.getenv('ADMIN_ID')
    return admin_id and str(user_id) == str(admin_id)

# Valyuta tanlash tugmalari
def get_currency_keyboard():
    return ReplyKeyboardMarkup([
        ["💵 USD", "🇺🇿 So'm"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

def get_admin_keyboard():
    return ReplyKeyboardMarkup([
        ["📦 Mahsulot Qo'shish", "🗑️ Mahsulot O'chirish"],
        ["👥 Foydalanuvchilar", "📊 Statistika"],
        ["🚫 Bloklash", "✅ Blokdan Ochish"],
        ["📋 Buyurtmalarni Boshqarish", "💰 To'lovlarni Boshqarish"],
        ["📢 Xabar Yuborish", "🤖 Avtomatik Xabarlar"],
        ["👤 Majburiy Ro'yxatdan O'tkazish", "🧹 Tozalash"],  # ✅ YANGI TUGMALAR
        ["🔴 Admin Paneldan Chiqish"]
    ], resize_keyboard=True)

# Mahsulot kategoriyalari
def get_categories_keyboard():
    return ReplyKeyboardMarkup([
        ["🏍️ MotoBike", "🛵 Scooter", "⚡ Electric Scooter"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

# Mahsulot o'chirish uchun kategoriyalar
def get_delete_categories_keyboard():
    return ReplyKeyboardMarkup([
        ["🏍️ MotoBike", "🛵 Scooter", "⚡ Electric Scooter"],
        ["📦 Barcha Mahsulotlar", "🔙 Orqaga"]
    ], resize_keyboard=True)

# MotoBike kategoriyalari
def get_motobike_categories_keyboard():
    return ReplyKeyboardMarkup([
        ["🛡️ Shlemlar", "👕 Moto Kiyimlar", "👞 Oyoq kiyimlari"],
        ["🦵 Oyoq Himoya", "🧤 Qo'lqoplar", "🎭 Yuz himoya"],
        ["🔧 MOTO EHTIYOT QISMLAR", "🔙 Orqaga"]
    ], resize_keyboard=True)

# MotoBike ehtiyot qismlari
def get_motobike_parts_keyboard():
    return ReplyKeyboardMarkup([
        ["⚙️ Sep", "🛞 Disca", "🦋 Parushka"],
        ["🛑 Tormoz Ruchkasi", "💡 Old Chiroqlar", "🔴 Orqa Chiroqlar"],
        ["🪑 O'tirgichlar", "🔇 Glushetillar", "🎛️ Gaz Troslari"],
        ["🔄 Sepleniya Ruchkalari", "⛽ Benzin baklar", "🔥 Svechalar"],
        ["⚡ Babinalar", "📦 Skores Karobkalari", "🔄 Karburator"],
        ["🛞 Apornik discalar", "🛑 Oldi-Orqa Klotkalar", "🎨 Tunning uchun Qismlar"],
        ["📦 Boshqa Ihtiyot Qismlari", "🔙 Orqaga"]
    ], resize_keyboard=True)

# Scooter kategoriyalari
def get_scooter_categories_keyboard():
    return ReplyKeyboardMarkup([
        ["⛽ Tank", "🚀 H Max", "⭐ Stell Max"],
        ["⚔️ Samuray", "🐅 Tiger", "🔧 Barcha Qismlar"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

# Electric Scooter kategoriyalari
def get_electric_scooter_categories_keyboard():
    return ReplyKeyboardMarkup([
        ["👹 Monster", "🐉 Drongo", "📦 Arenda"],
        ["💰 Vikup", "🔙 Orqaga"]
    ], resize_keyboard=True)

# Foydalanuvchilar ro'yxatini sahifalash uchun tugmalar
def get_users_pagination_keyboard(page=0, total_pages=1):
    keyboard = []
    
    if page > 0:
        keyboard.append(["⬅️ Oldingi sahifa"])
    
    if page < total_pages - 1:
        keyboard.append(["Keyingi sahifa ➡️"])
    
    # ✅ BOG'LANISH tugmasi qo'shildi
    keyboard.append(["📞 Foydalanuvchi bilan Bog'lanish"])
    keyboard.append(["🔙 Orqaga"])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Rasmlarni saqlash tugmalari
def get_photos_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ Rasmlarni Saqlash", "🔄 Rasmlarni Qayta Yuklash"],
        ["📦 Rassmsiz Saqlash", "🔙 Orqaga"]
    ], resize_keyboard=True)

# Mahsulot o'chirish uchun tasdiqlash tugmalari
def get_delete_confirmation_keyboard():
    return ReplyKeyboardMarkup([
        ["✅ HA, O'chirish", "❌ Yo'q, Bekor Qilish"]
    ], resize_keyboard=True)

# Mahsulotlarni sahifalash tugmalari
def get_products_pagination_keyboard(page=0, total_pages=1, has_products=True):
    keyboard = []
    
    if has_products:
        if page > 0:
            keyboard.append(["⬅️ Oldingi sahifa"])
        
        if page < total_pages - 1:
            keyboard.append(["Keyingi sahifa ➡️"])
    
    keyboard.append(["🗑️ Mahsulotni O'chirish", "🔙 Orqaga"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Buyurtma boshqarish tugmalari
def get_order_management_keyboard():
    return ReplyKeyboardMarkup([
        ["📋 Kutayotgan Buyurtmalar", "💰 Kutayotgan To'lovlar"],
        ["✅ Buyurtmani Tasdiqlash", "❌ Buyurtmani Rad Etish"],
        ["✅ To'lovni Tasdiqlash", "❌ To'lovni Rad Etish"],
        ["⚠️ Sohta Chek Deb Belgilash", "🔙 Orqaga"]
    ], resize_keyboard=True)
    
# admin.py ga yangi funksiya:
async def force_register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini majburiy ro'yxatdan o'tkazish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👤 **Foydalanuvchini majburiy ro'yxatdan o'tkazish**\n\n"
        "Foydalanuvchi ID sini kiriting:\n\n"
        "Masalan: `1076971821`",
        reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
        parse_mode='Markdown'
    )
    context.user_data['action'] = 'force_register'
    return ADMIN_MAIN


async def admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    text = update.message.text
    
    # DEBUG: Nima yozayotganingizni ko'ramiz
    logger.info(f"Admin main: text='{text}', action={context.user_data.get('action')}")
    
    # 1. BEKOR QILISH tugmasi - birinchi tekshirish
    if text == "❌ Bekor qilish":
        context.user_data.clear()
        await update.message.reply_text(
            "✅ **Amal bekor qilindi!**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return ADMIN_MAIN
    
    # 2. FORCE REGISTER bosqichi
    elif context.user_data.get('action') == 'force_register':
        try:
            target_user_id = int(text)
            
            # Foydalanuvchini ro'yxatdan o'tkazish
            db.update_user(target_user_id, registered=True)
            
            # Foydalanuvchiga xabar yuborish
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="✅ **Siz admin tomonidan ro'yxatdan o'tkazildingiz!**\n\n"
                         "Endi botdan to'liq foydalanishingiz mumkin.\n"
                         "/start buyrug'i orqali asosiy menyuga o'ting."
                )
            except Exception as e:
                logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                f"✅ **Foydalanuvchi** `{target_user_id}` **ro'yxatdan o'tkazildi!**",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            
            context.user_data.clear()
            return ADMIN_MAIN
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Noto'g'ri ID format!**\n\n"
                "Faqat raqamlardan foydalaning.",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
    
    # 3. XABAR YUBORISH bosqichi
    elif context.user_data.get('action') == 'send_message_to_customer':
        target_user_id = context.user_data.get('contact_user_id')
        
        if not target_user_id:
            await update.message.reply_text(
                "❌ **Foydalanuvchi ID si topilmadi!**\n\n"
                "Qaytadan boshlang.",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            context.user_data.clear()
            return ADMIN_MAIN
        
        # Xabar uzunligini tekshirish
        if len(text.strip()) < 2:
            await update.message.reply_text(
                "❌ **Xabar juda qisqa!**\n\n"
                "Iltimos, kamida 2 belgidan iborat xabar yuboring.",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
        
        # Foydalanuvchiga xabar yuborish
        try:
            # Foydalanuvchi mavjudligini tekshirish
            user_info = db.get_user(target_user_id)
            if not user_info:
                await update.message.reply_text(
                    f"❌ **Foydalanuvchi topilmadi!**\n\n"
                    f"ID: `{target_user_id}`",
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
                context.user_data.clear()
                return ADMIN_MAIN
            
            # Xabar yuborish
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"📨 **Admin xabari:**\n\n{text}"
            )
            
            await update.message.reply_text(
                f"✅ **Xabar muvaffaqiyatli yuborildi!**\n\n"
                f"👤 **Foydalanuvchi ID:** `{target_user_id}`\n"
                f"📝 **Xabar:** {text}",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Admin xabar yubordi: admin_id={user_id}, target_id={target_user_id}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Xabar yuborishda xatolik: {error_msg}")
            
            await update.message.reply_text(
                f"❌ **Xabar yuborishda xatolik!**\n\n"
                f"👤 Foydalanuvchi ID: `{target_user_id}`\n\n"
                f"❌ **Xatolik:** {error_msg}\n\n"
                f"Foydalanuvchi botni bloklagan yoki mavjud emas.",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
        
        # User datani tozalash
        context.user_data.clear()
        return ADMIN_MAIN
    
    # 4. BROADCAST XABAR bosqichi
    elif context.user_data.get('action') == 'broadcast_message':
        # Bu yerda faqat context.user_data['broadcast_message'] ni saqlaymiz
        # Haqiqiy yuborish keyinroq
        context.user_data['broadcast_message'] = text
        
        # Tasdiqlash so'raymiz
        await update.message.reply_text(
            f"⚠️ **BARCHA FOYDALANUVCHILARGA XABAR YUBORISH** ⚠️\n\n"
            f"📝 **Xabar matni:**\n{text}\n\n"
            f"📊 **Foydalanuvchilar soni:** {len(db.get_all_users())} ta\n\n"
            f"❓ **Rostdan ham barcha foydalanuvchilarga shu xabarni yubormoqchimisiz?**",
            reply_markup=ReplyKeyboardMarkup([
                ["✅ HA, Yuborish", "❌ Yo'q, Bekor qilish"]
            ], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'confirm_broadcast'
        return ADMIN_MAIN
    
    # 5. BROADCAST TASDIQLASH
    elif context.user_data.get('action') == 'confirm_broadcast':
        if text == "✅ HA, Yuborish":
            message_text = context.user_data.get('broadcast_message', '')
            
            if not message_text:
                await update.message.reply_text(
                    "❌ **Xabar matni topilmadi!**",
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
                context.user_data.clear()
                return ADMIN_MAIN
            
            # Xabarni yuborishni boshlaymiz
            await process_broadcast_message(update, context, message_text)
            
            # User datani tozalash
            context.user_data.clear()
            return ADMIN_MAIN
            
        elif text == "❌ Yo'q, Bekor qilish":
            await update.message.reply_text(
                "✅ **Xabar yuborish bekor qilindi!**",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            context.user_data.clear()
            return ADMIN_MAIN
    
    # 6. ACTION handler (bloklash, bog'lanish)
    elif 'action' in context.user_data:
        action = context.user_data['action']
        
        # ID ni tekshirish
        try:
            target_user_id = int(text)
        except ValueError:
            await update.message.reply_text(
                "❌ **Iltimos, to'g'ri foydalanuvchi ID sini kiriting!**\n\n"
                "Faqat raqamlardan iborat bo'lishi kerak.\n"
                "Masalan: `8083596990`",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
        
        if action == 'block':
            await block_user_with_message(update, context, target_user_id)
            context.user_data.clear()
            return ADMIN_MAIN
        
        elif action == 'unblock':
            await unblock_user_with_message(update, context, target_user_id)
            context.user_data.clear()
            return ADMIN_MAIN
        
        elif action == 'contact_customer':
            # Mijoz bilan bog'lanish - ID ni saqlaymiz
            context.user_data['contact_user_id'] = target_user_id
            context.user_data['action'] = 'send_message_to_customer'
            
            await update.message.reply_text(
                f"👤 **Mijoz bilan bog'lanish**\n\n"
                f"✅ **Foydalanuvchi ID qabul qilindi:** `{target_user_id}`\n\n"
                f"📝 **Endi xabaringizni yuboring:**\n\n"
                f"Xabar yuborilgach, avtomatik admin panelga qaytasiz.\n"
                f"Bekor qilish uchun '❌ Bekor qilish' tugmasini bosing.",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
    
    # 7. Asosiy menyu tugmalari
    elif text == "📦 Mahsulot Qo'shish":
        return await start_add_product(update, context)
    
    elif text == "🗑️ Mahsulot O'chirish":
        return await start_delete_product(update, context)
    
    elif text == "👥 Foydalanuvchilar":
        return await show_users_list(update, context)
    
    elif text == "📊 Statistika":
        total_users = len(db.get_all_users())
        total_products = len(db.get_all_products())
        total_orders = len(db.get_orders())
        
        motobike_products = len(db.get_products_by_category_only("🏍️ MotoBike"))
        scooter_products = len(db.get_products_by_category_only("🛵 Scooter"))
        electric_products = len(db.get_products_by_category_only("⚡ Electric Scooter"))
        
        stats_message = (
            "📊 **Bot Statistikasi**\n\n"
            f"👥 **Foydalanuvchilar:** {total_users} ta\n"
            f"📦 **Jami mahsulotlar:** {total_products} ta\n"
            f"📋 **Buyurtmalar:** {total_orders} ta\n\n"
            f"**Kategoriyalar bo'yicha:**\n"
            f"🏍️ **MotoBike:** {motobike_products} ta\n"
            f"🛵 **Scooter:** {scooter_products} ta\n"
            f"⚡ **Electric Scooter:** {electric_products} ta\n"
        )
        
        await update.message.reply_text(
            stats_message,
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    elif text == "🚫 Bloklash":
        await update.message.reply_text(
            "🚫 **Bloklash**\n\nFoydalanuvchi ID sini yuboring:\n\nMasalan: `8083596990`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'block'
    
    elif text == "✅ Blokdan Ochish":
        await update.message.reply_text(
            "✅ **Blokdan ochish**\n\nFoydalanuvchi ID sini yuboring:\n\nMasalan: `8083596990`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'unblock'
    
    elif text == "📋 Buyurtmalarni Boshqarish":
        await update.message.reply_text(
            "📋 **Buyurtma va To'lov Boshqaruvi**\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=get_order_management_keyboard(),
            parse_mode='Markdown'
        )
        return ORDER_MANAGEMENT
    
    elif text == "💰 To'lovlarni Boshqarish":
        await update.message.reply_text(
            "💰 **To'lov Boshqaruvi**\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=get_order_management_keyboard(),
            parse_mode='Markdown'
        )
        return ORDER_MANAGEMENT
    
    elif text == "📞 Foydalanuvchi bilan Bog'lanish":
        await update.message.reply_text(
            "👤 **Foydalanuvchi bilan bog'lanish**\n\n"
            "Foydalanuvchi ID sini kiriting:\n\n"
            "Masalan: `8083596990`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'contact_customer'
    
    elif text == "📢 Xabar Yuborish":
        return await send_broadcast_message(update, context)
    
    elif text == "⬅️ Oldingi sahifa":
        page = context.user_data.get('users_page', 0)
        if page > 0:
            context.user_data['users_page'] = page - 1
            await show_users_page(update, context)
    
    elif text == "Keyingi sahifa ➡️":
        page = context.user_data.get('users_page', 0)
        total_pages = context.user_data.get('total_pages', 1)
        if page < total_pages - 1:
            context.user_data['users_page'] = page + 1
            await show_users_page(update, context)
    
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "👨‍💼 **Admin Panel**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    elif text == "🔴 Admin Paneldan Chiqish":
        await update.message.reply_text(
            "👋 **Admin paneldan chiqdingiz!**\n\n"
            "Qaytish uchun /admin yoki /start buyrug'ini yuboring.",
            reply_markup=ReplyKeyboardMarkup([["/start"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # YANGI TUGMALAR
    elif text == "👤 Majburiy Ro'yxatdan O'tkazish":
        await update.message.reply_text(
            "👤 **Foydalanuvchini majburiy ro'yxatdan o'tkazish**\n\n"
            "Foydalanuvchi ID sini kiriting:\n\n"
            "Masalan: `1076971821`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'force_register'
    
    elif text == "🤖 Avtomatik Xabarlar":
        return await yearly_messenger_control(update, context)
    
    elif text == "🧹 Tozalash":
        deleted = db.clean_unregistered_users(1)
        await update.message.reply_text(
            f"🧹 **Tozalash yakunlandi!**\n\n"
            f"✅ {deleted} ta ro'yxatdan o'tmagan foydalanuvchi o'chirildi.",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    # Agar boshqa narsa yozilsa
    else:
        await update.message.reply_text(
            "🤔 **Noma'lum buyruq!**\n\n"
            "Iltimos, menyudan tugmalardan birini tanlang.",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    return ADMIN_MAIN

# Admin start komandasi
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    # User datani tozalash
    context.user_data.clear()
    
    await update.message.reply_text(
        "👨‍💼 **Admin Panelga Xush Kelibsiz!**\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=get_admin_keyboard(),
        parse_mode='Markdown'
    )
    return ADMIN_MAIN

# Mahsulot qo'shishni boshlash
async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Oldingi ma'lumotlarni tozalash
    context.user_data.pop('product_photos', None)
    
    await update.message.reply_text(
        "📦 **Mahsulot qo'shish**\n\n"
        "Kategoriyani tanlang:",
        reply_markup=get_categories_keyboard(),
        parse_mode='Markdown'
    )
    return ADD_PRODUCT_CATEGORY

# Kategoriyani tanlash
async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['product_category'] = text
    
    if text == "🏍️ MotoBike":
        await update.message.reply_text(
            "🏍️ **MotoBike kategoriyasi**\n\n"
            "Pastki kategoriyani tanlang:",
            reply_markup=get_motobike_categories_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_SUBCATEGORY
    
    elif text == "🛵 Scooter":
        await update.message.reply_text(
            "🛵 **Scooter kategoriyasi**\n\n"
            "Scooter modelini tanlang:",
            reply_markup=get_scooter_categories_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_SUBCATEGORY
    
    elif text == "⚡ Electric Scooter":
        await update.message.reply_text(
            "⚡ **Electric Scooter kategoriyasi**\n\n"
            "Pastki kategoriyani tanlang:",
            reply_markup=get_electric_scooter_categories_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_SUBCATEGORY
    
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "👨‍💼 **Admin Panel**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return ADMIN_MAIN
    
    return ADD_PRODUCT_CATEGORY

# Pastki kategoriyani tanlash
async def choose_subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['product_subcategory'] = text
    
    # Agar MOTO EHTIYOT QISMLAR tanlangan bo'lsa
    if text == "🔧 MOTO EHTIYOT QISMLAR":
        await update.message.reply_text(
            "🔧 **Moto Ehtiyot Qismlari**\n\n"
            "Qismni tanlang:",
            reply_markup=get_motobike_parts_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_NAME
    
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "📦 **Mahsulot qo'shish**\n\n"
            "Kategoriyani tanlang:",
            reply_markup=get_categories_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_CATEGORY
    
    else:
        await update.message.reply_text(
            "✍️ **Mahsulot nomini kiriting:**\n\n"
            "Masalan: 'HD Helm' yoki 'Sport Qo'lqop'",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_NAME

# Mahsulot nomini qabul qilish
async def get_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 Orqaga":
        category = context.user_data.get('product_category')
        if category == "🏍️ MotoBike":
            await update.message.reply_text(
                "🏍️ **MotoBike kategoriyasi**\n\n"
                "Pastki kategoriyani tanlang:",
                reply_markup=get_motobike_categories_keyboard(),
                parse_mode='Markdown'
            )
            return ADD_PRODUCT_SUBCATEGORY
        else:
            await update.message.reply_text(
                "📦 **Mahsulot qo'shish**\n\n"
                "Kategoriyani tanlang:",
                reply_markup=get_categories_keyboard(),
                parse_mode='Markdown'
            )
            return ADD_PRODUCT_CATEGORY
    
    context.user_data['product_name'] = text
    await update.message.reply_text(
        "💰 **Valyuta turini tanlang:**",
        reply_markup=get_currency_keyboard(),
        parse_mode='Markdown'
    )
    return ADD_PRODUCT_PRICE_TYPE

# Valyuta turini tanlash
async def choose_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            "✍️ **Mahsulot nomini kiriting:**\n\n"
            "Masalan: 'HD Helm' yoki 'Sport Qo'lqop'",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_NAME
    
    context.user_data['currency'] = text
    currency_symbol = "$" if text == "💵 USD" else "so'm"
    
    await update.message.reply_text(
        f"💰 **Mahsulot narxini kiriting ({currency_symbol}):**\n\n"
        f"Masalan: 150 yoki 250 (agar USD bo'lsa)\n"
        f"Masalan: 150000 yoki 250000 (agar so'm bo'lsa)",
        reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
        parse_mode='Markdown'
    )
    return ADD_PRODUCT_PRICE

# Mahsulot narxini qabul qilish
async def get_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            "💰 **Valyuta turini tanlang:**",
            reply_markup=get_currency_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_PRICE_TYPE
    
    try:
        price = float(text)
        currency = context.user_data.get('currency', '🇺🇿 So\'m')
        context.user_data['product_price'] = price
        context.user_data['product_currency'] = currency
        
        await update.message.reply_text(
            "📝 **Mahsulot tavsifini kiriting:**\n\n"
            "Masalan: 'Yuqori sifatli mototsikl shlemi'",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_DESC
    except ValueError:
        currency = context.user_data.get('currency', '🇺🇿 So\'m')
        currency_symbol = "$" if currency == "💵 USD" else "so'm"
        
        await update.message.reply_text(
            f"❌ **Noto'g'ri narx format!**\n\n"
            f"Iltimos, faqat raqamlardan foydalaning.\n"
            f"Masalan: 150 yoki 250 (agar USD bo'lsa)\n"
            f"Masalan: 150000 yoki 250000 (agar so'm bo'lsa)",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_PRICE

# Mahsulot tavsifini qabul qilish
async def get_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 Orqaga":
        currency = context.user_data.get('currency', '🇺🇿 So\'m')
        currency_symbol = "$" if currency == "💵 USD" else "so'm"
        
        await update.message.reply_text(
            f"💰 **Mahsulot narxini kiriting ({currency_symbol}):**\n\n"
            f"Masalan: 150 yoki 250 (agar USD bo'lsa)\n"
            f"Masalan: 150000 yoki 250000 (agar so'm bo'lsa)",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_PRICE
    
    context.user_data['product_description'] = text
    
    await update.message.reply_text(
        "🖼️ **Mahsulot rasmlarini yuboring:**\n\n"
        "✅ **Ixtiyoriy:** 1 ta, 2 ta yoki ko'proq rasm yuborishingiz mumkin\n"
        "📸 **Qo'shimcha:** Bir nechta rasmlarni bir vaqtda yuborishingiz mumkin\n"
        "⏰ **Keyin:** Rasmlarni yuborgach, tugmalardan birini bosing\n\n"
        "**Tugmalar:**\n"
        "• ✅ Rasmlarni Saqlash - hozirgi rasmlar bilan saqlash\n"
        "• 🔄 Rasmlarni Qayta Yuklash - barcha rasmlarni o'chirib yangilash\n"
        "• 📦 Rassmsiz Saqlash - rasmsiz saqlash\n"
        "• 🔙 Orqaga - oldingi qadamga qaytish",
        reply_markup=get_photos_keyboard(),
        parse_mode='Markdown'
    )
    return ADD_PRODUCT_PHOTOS

# Mahsulotni saqlash
async def save_product(update: Update, context: ContextTypes.DEFAULT_TYPE, photos):
    # Ma'lumotlarni olish
    category = context.user_data.get('product_category', '')
    subcategory = context.user_data.get('product_subcategory', '')
    name = context.user_data.get('product_name', '')
    price = context.user_data.get('product_price', 0)
    currency = context.user_data.get('product_currency', '🇺🇿 So\'m')
    description = context.user_data.get('product_description', '')
    
    # Narxni formatlash
    if currency == "💵 USD":
        price_display = f"${price:,.0f}"
        price_in_som = price * 12500  # USD dan so'm ga o'tkazish (taxminiy)
    else:
        price_display = f"{price:,.0f} so'm"
        price_in_som = price
    
    # Rasmlarni saqlash
    photos_str = str(photos) if photos else "[]"
    
    # Ma'lumotlarni saqlash
    success = db.add_product(category, subcategory, name, price_in_som, description, photos_str)
    
    if success:
        message = (
            f"✅ **Mahsulot muvaffaqiyatli qo'shildi!**\n\n"
            f"🏷️ **Kategoriya:** {category}\n"
            f"📂 **Pastki kategoriya:** {subcategory}\n"
            f"📦 **Nomi:** {name}\n"
            f"💰 **Narxi:** {price_display}\n"
            f"📝 **Tavsif:** {description}\n"
            f"🖼️ **Rasmlar:** {len(photos)} ta\n\n"
            f"💡 **Eslatma:** Mahsulot foydalanuvchilarga ko'rsatiladi!"
        )
        
        # Agar rasmlar bo'lsa, ularni yuborish
        if photos:
            try:
                # Birinchi rasmni yuborish
                await update.message.reply_photo(
                    photo=photos[0],
                    caption=message,
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
                
                # Qolgan rasmlarni alohida yuborish
                for i, photo_id in enumerate(photos[1:], 2):
                    await update.message.reply_photo(
                        photo=photo_id,
                        caption=f"🖼️ Rasm {i} - {name}"
                    )
            except Exception as e:
                logger.error(f"Rasm yuborishda xatolik: {e}")
                await update.message.reply_text(
                    message,
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                message,
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            "❌ **Mahsulot qo'shishda xatolik!**\n\n"
            "Iltimos, qaytadan urinib ko'ring.",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    # User datani tozalash
    context.user_data.clear()
    return ADMIN_MAIN

# Mahsulot rasmlarini qabul qilish
async def get_product_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message.text else ""
    
    # Rasmlarni saqlash tugmasi
    if text == "✅ Rasmlarni Saqlash":
        photos = context.user_data.get('product_photos', [])
        if photos:
            # FAQRAT UNIQUE RASMLARNI SAQLAYMIZ
            unique_photos = list(set(photos))  # Takrorlangan rasmlarni olib tashlaymiz
            return await save_product(update, context, photos=unique_photos)
        else:
            await update.message.reply_text(
                "❌ **Hali hech qanday rasm yuborilmadi!**\n\n"
                "Iltimos, avval rasmlarni yuboring yoki '📦 Rassmsiz Saqlash' tugmasini bosing.",
                reply_markup=get_photos_keyboard(),
                parse_mode='Markdown'
            )
            return ADD_PRODUCT_PHOTOS
    
    # Rasmlarni qayta yuklash tugmasi
    elif text == "🔄 Rasmlarni Qayta Yuklash":
        context.user_data['product_photos'] = []
        await update.message.reply_text(
            "🔄 **Barcha rasmlar o'chirildi!**\n\n"
            "Endi yangi rasmlarni yuboring:",
            reply_markup=get_photos_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_PHOTOS
    
    # Rasmsiz saqlash tugmasi
    elif text == "📦 Rassmsiz Saqlash":
        return await save_product(update, context, photos=[])
    
    # Orqaga tugmasi
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "📝 **Mahsulot tavsifini kiriting:**\n\n"
            "Masalan: 'Yuqori sifatli mototsikl shlemi'",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_DESC
    
    # Rasm yuborilgan holat - FAQRAT ENG YUQORI SIFATLI RASMNI SAQLAYMIZ
    elif update.message.photo:
        photos = context.user_data.get('product_photos', [])
        
        # Bir nechta rasm yuborilgan bo'lishi mumkin, faqat eng yuqori sifatlisini olamiz
        if update.message.photo:
            # Eng yuqori sifatli rasm (oxirgi element)
            highest_quality_photo = update.message.photo[-1]
            photos.append(highest_quality_photo.file_id)
        
        # Takrorlangan rasmlarni olib tashlaymiz
        unique_photos = list(set(photos))
        context.user_data['product_photos'] = unique_photos
        
        await update.message.reply_text(
            f"✅ **{len(unique_photos)} ta rasm qabul qilindi!**\n\n"
            f"📸 **Yuklangan rasmlar soni:** {len(unique_photos)}\n\n"
            f"**Keyingi amalni tanlang:**\n"
            f"• ✅ Rasmlarni Saqlash - mahsulotni rasmlar bilan saqlash\n"
            f"• 🔄 Rasmlarni Qayta Yuklash - barcha rasmlarni o'chirish\n"
            f"• 📦 Rassmsiz Saqlash - rasmsiz saqlash\n"
            f"• 🔙 Orqaga - oldingi qadamga qaytish\n\n"
            f"💡 **Eslatma:** Yana rasm yuborishingiz mumkin yoki tugmalardan birini bosing.",
            reply_markup=get_photos_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_PHOTOS
    
    # Rasm yuborilmagan holat
    else:
        await update.message.reply_text(
            "🖼️ **Iltimos, rasm yuboring yoki tugmalardan birini tanlang!**\n\n"
            "✅ **Ixtiyoriy:** 1 ta, 2 ta yoki ko'proq rasm yuborishingiz mumkin\n"
            "📸 **Qo'shimcha:** Bir nechta rasmlarni bir vaqtda yuborishingiz mumkin\n\n"
            "**Tugmalar:**\n"
            "• ✅ Rasmlarni Saqlash - hozirgi rasmlar bilan saqlash\n"
            "• 🔄 Rasmlarni Qayta Yuklash - barcha rasmlarni o'chirib yangilash\n"
            "• 📦 Rassmsiz Saqlash - rasmsiz saqlash\n"
            "• 🔙 Orqaga - oldingi qadamga qaytish",
            reply_markup=get_photos_keyboard(),
            parse_mode='Markdown'
        )
        return ADD_PRODUCT_PHOTOS

# ==================== MAHSULOT O'CHIRISH QISMI ====================

# Mahsulot o'chirishni boshlash
async def start_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User datani tozalash
    context.user_data.pop('delete_category', None)
    context.user_data.pop('delete_product_id', None)
    context.user_data.pop('products_page', None)
    
    await update.message.reply_text(
        "🗑️ **Mahsulot o'chirish**\n\n"
        "O'chirmoqchi bo'lgan mahsulotlaringiz kategoriyasini tanlang:",
        reply_markup=get_delete_categories_keyboard(),
        parse_mode='Markdown'
    )
    return DELETE_PRODUCT_CATEGORY

# O'chirish uchun kategoriyani tanlash
async def choose_delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 Orqaga":
        await update.message.reply_text(
            "👨‍💼 **Admin Panel**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return ADMIN_MAIN
    
    context.user_data['delete_category'] = text
    context.user_data['products_page'] = 0
    
    # Kategoriya bo'yicha mahsulotlarni olish
    if text == "📦 Barcha Mahsulotlar":
        products = db.get_all_products()
        category_name = "Barcha Mahsulotlar"
    else:
        products = db.get_products_by_category_only(text)
        category_name = text
    
    if not products:
        await update.message.reply_text(
            f"❌ **{category_name} bo'limida mahsulot topilmadi!**\n\n"
            "Boshqa kategoriyani tanlang:",
            reply_markup=get_delete_categories_keyboard(),
            parse_mode='Markdown'
        )
        return DELETE_PRODUCT_CATEGORY
    
    # Mahsulotlarni sahifalab ko'rsatish
    await show_products_for_deletion(update, context, products, category_name)
    return DELETE_PRODUCT_SELECT

# O'chirish uchun mahsulotlarni ko'rsatish
async def show_products_for_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE, products, category_name):
    page = context.user_data.get('products_page', 0)
    products_per_page = 3
    total_pages = (len(products) + products_per_page - 1) // products_per_page
    
    start_idx = page * products_per_page
    end_idx = start_idx + products_per_page
    current_products = products[start_idx:end_idx]
    
    message = f"🗑️ **{category_name} - Mahsulotlar Ro'yxati**\n\n"
    message += f"📄 **Sahifa:** {page + 1}/{total_pages}\n\n"
    
    for i, product in enumerate(current_products, start_idx + 1):
        # Mahsulot ma'lumotlarini xavfsiz olish
        if len(product) >= 8:
            product_id, category, subcategory, name, price, description, image, available = product
        else:
            continue
        
        # Narxni formatlash
        price_formatted = f"{price:,.0f} so'm" if price else "Narx ko'rsatilmagan"
        
        # Kategoriya va subcategory ni formatlash
        category_display = category if category else "Noma'lum"
        subcategory_display = subcategory if subcategory else "Noma'lum"
        
        message += (
            f"🆔 **ID:** `{product_id}`\n"
            f"🏷️ **Nomi:** {name or 'Nomsiz'}\n"
            f"📂 **Kategoriya:** {category_display} -> {subcategory_display}\n"
            f"💰 **Narxi:** {price_formatted}\n"
            f"📦 **Holat:** {'✅ Mavjud' if available else '❌ Mavjud emas'}\n"
            f"────────────────────\n\n"
        )
    
    if not current_products:
        message += "❌ **Bu sahifada mahsulotlar topilmadi**\n\n"
    
    context.user_data['current_products'] = products
    context.user_data['total_pages'] = total_pages
    
    await update.message.reply_text(
        message,
        reply_markup=get_products_pagination_keyboard(page, total_pages, len(products) > 0),
        parse_mode='Markdown'
    )

# Mahsulot o'chirish sahifalash
async def delete_product_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    page = context.user_data.get('products_page', 0)
    total_pages = context.user_data.get('total_pages', 1)
    products = context.user_data.get('current_products', [])
    category = context.user_data.get('delete_category', '')
    
    if text == "⬅️ Oldingi sahifa" and page > 0:
        context.user_data['products_page'] = page - 1
    elif text == "Keyingi sahifa ➡️" and page < total_pages - 1:
        context.user_data['products_page'] = page + 1
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "🗑️ **Mahsulot o'chirish**\n\n"
            "O'chirmoqchi bo'lgan mahsulotlaringiz kategoriyasini tanlang:",
            reply_markup=get_delete_categories_keyboard(),
            parse_mode='Markdown'
        )
        return DELETE_PRODUCT_CATEGORY
    elif text == "🗑️ Mahsulotni O'chirish":
        await update.message.reply_text(
            "✍️ **O'chirmoqchi bo'lgan mahsulot ID sini kiriting:**\n\n"
            "Yuqoridagi ro'yxatdan mahsulot ID sini ko'chiring:\n\n"
            "Masalan: `15` yoki `23`",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return DELETE_PRODUCT_SELECT
    
    await show_products_for_deletion(update, context, products, category)
    return DELETE_PRODUCT_SELECT

# Mahsulot ID sini qabul qilish
async def get_product_id_for_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 Orqaga":
        # Sahifaga qaytish
        products = context.user_data.get('current_products', [])
        category = context.user_data.get('delete_category', '')
        await show_products_for_deletion(update, context, products, category)
        return DELETE_PRODUCT_SELECT
    
    # Mahsulot ID sini tekshirish
    try:
        product_id = int(text)
        
        # Ma'lumotlar bazasidan mahsulotni tekshirish
        product = db.get_product_by_id(product_id)
        if not product:
            await update.message.reply_text(
                f"❌ **{product_id} ID li mahsulot topilmadi!**\n\n"
                "Iltimos, to'g'ri mahsulot ID sini kiriting:",
                reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return DELETE_PRODUCT_SELECT
        
        # Mahsulot ma'lumotlarini saqlash
        context.user_data['delete_product_id'] = product_id
        context.user_data['delete_product_info'] = product
        
        # Mahsulot ma'lumotlarini xavfsiz olish
        if len(product) >= 8:
            product_id, category, subcategory, name, price, description, image, available = product
        else:
            await update.message.reply_text(
                "❌ **Mahsulot ma'lumotlari to'liq emas!**",
                reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return DELETE_PRODUCT_SELECT
        
        price_formatted = f"{price:,.0f} so'm" if price else "Narx ko'rsatilmagan"
        
        # Tavsifni formatlash
        description_display = ""
        if description:
            if len(description) > 100:
                description_display = description[:100] + "..."
            else:
                description_display = description
        else:
            description_display = "Tavsif yo'q"
        
        # Kategoriya va subcategory ni formatlash
        category_display = category if category else "Noma'lum"
        subcategory_display = subcategory if subcategory else "Noma'lum"
        
        confirmation_message = (
            f"⚠️ **MAHSULOTNI O'CHIRISH** ⚠️\n\n"
            f"Quyidagi mahsulotni o'chirmoqchimisiz?\n\n"
            f"🆔 **ID:** `{product_id}`\n"
            f"🏷️ **Nomi:** {name or 'Nomsiz'}\n"
            f"📂 **Kategoriya:** {category_display} -> {subcategory_display}\n"
            f"💰 **Narxi:** {price_formatted}\n"
            f"📝 **Tavsif:** {description_display}\n"
            f"📦 **Holat:** {'✅ Mavjud' if available else '❌ Mavjud emas'}\n\n"
            f"❌ **Diqqat! Bu amalni ortga qaytarib bo'lmaydi!**"
        )
        
        await update.message.reply_text(
            confirmation_message,
            reply_markup=get_delete_confirmation_keyboard(),
            parse_mode='Markdown'
        )
        return DELETE_PRODUCT_CONFIRM
        
    except ValueError:
        await update.message.reply_text(
            "❌ **Noto'g'ri ID format!**\n\n"
            "Iltimos, faqat raqamlardan iborat mahsulot ID sini kiriting:\n\n"
            "Masalan: `15` yoki `23`",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return DELETE_PRODUCT_SELECT

# Mahsulotni o'chirishni tasdiqlash
async def confirm_product_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ Yo'q, Bekor Qilish":
        await update.message.reply_text(
            "✅ **Mahsulot o'chirish bekor qilindi!**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return ADMIN_MAIN
    
    elif text == "✅ HA, O'chirish":
        product_id = context.user_data.get('delete_product_id')
        product_info = context.user_data.get('delete_product_info')
        
        if product_id and product_info:
            # Mahsulotni ma'lumotlar bazasidan o'chirish
            success = db.delete_product(product_id)
            
            if success:
                product_name = product_info[3]  # name maydoni
                await update.message.reply_text(
                    f"✅ **Mahsulot muvaffaqiyatli o'chirildi!**\n\n"
                    f"🗑️ **O'chirilgan mahsulot:** {product_name}\n"
                    f"🆔 **ID:** `{product_id}`",
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ **Mahsulotni o'chirishda xatolik!**\n\n"
                    f"Iltimos, qaytadan urinib ko'ring.",
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                "❌ **Mahsulot ma'lumotlari topilmadi!**",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
        
        return ADMIN_MAIN
    
    return DELETE_PRODUCT_CONFIRM

# ==================== BLOKLASH FUNKSIYALARI ====================

# Bloklash funksiyasi - XABAR YUBORISH QO'SHILDI
async def block_user_with_message(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user_id):
    """Foydalanuvchini bloklash va xabar yuborish"""
    try:
        # Foydalanuvchini bloklash
        success = db.block_user(target_user_id)
        
        if success:
            # Bloklangan foydalanuvchiga xabar yuborish
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="❌ **Siz bloklandingiz!**\n\n"
                         "Botdan foydalanish huquqingiz cheklangan.\n"
                         "Agar bu xato deb hisoblasangiz, admin bilan bog'laning:\n"
                         "👤 @Operator_Kino_1985\n"
                         "📞 +998(98)8882505"
                )
            except Exception as e:
                logger.error(f"Bloklangan foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                f"✅ **Foydalanuvchi** `{target_user_id}` **muvaffaqiyatli bloklandi!**\n\n"
                f"📩 Bloklanganlik haqida xabar yuborildi.",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Foydalanuvchi** `{target_user_id}` **ni bloklashda xatolik!**",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Bloklash jarayonida xatolik: {e}")
        await update.message.reply_text(
            f"❌ **Bloklashda xatolik!**\n\n{e}",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )

# Blokdan ochish funksiyasi - XABAR YUBORISH QO'SHILDI
async def unblock_user_with_message(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user_id):
    """Foydalanuvchini blokdan ochish va xabar yuborish"""
    try:
        # Foydalanuvchini blokdan ochish
        success = db.unblock_user(target_user_id)
        
        if success:
            # Blokdan ochilgan foydalanuvchiga xabar yuborish
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="✅ **Siz blokdan ochildingiz!**\n\n"
                         "Botdan foydalanish huquqingiz qayta tiklandi.\n"
                         "/start buyrug'i orqali botdan foydalanishni davom ettirishingiz mumkin.\n\n"
                         "📞 Qo'llab-quvvatlash: @Operator_Kino_1985\n"
                         "☎️ Telefon: +998(98)8882505"
                )
            except Exception as e:
                logger.error(f"Blokdan ochilgan foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                f"✅ **Foydalanuvchi** `{target_user_id}` **blokdan ochildi!**\n\n"
                f"📩 Blokdan ochilganlik haqida xabar yuborildi.",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Foydalanuvchi** `{target_user_id}` **ni blokdan ochishda xatolik!**",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Blokdan ochish jarayonida xatolik: {e}")
        await update.message.reply_text(
            f"❌ **Blokdan ochishda xatolik!**\n\n{e}",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        
# ==================== MIJOZ BILAN BOG'LANISH ====================

async def contact_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mijoz bilan avtomatik bog'lanish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👤 **Mijoz bilan avtomatik bog'lanish**\n\n"
        "Mijoz ID sini kiriting:\n\n"
        "Masalan: `123456789`",
        reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
        parse_mode='Markdown'
    )
    context.user_data['action'] = 'contact_customer_auto'      

# ==================== BUYURTMA VA TO'LOV BOSHQARISH ====================

# Buyurtma boshqarish
async def order_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    text = update.message.text
    
    if text == "📋 Kutayotgan Buyurtmalar":
        orders = db.get_pending_orders()
        if orders:
            message = "⏳ **Kutayotgan Buyurtmalar:**\n\n"
            for order in orders[:10]:
                order_id, user_name, phone, product_name, quantity, order_date, status = order
                message += (
                    f"🆔 **Buyurtma:** #{order_id}\n"
                    f"👤 **Mijoz:** {user_name}\n"
                    f"📞 **Tel:** {phone}\n"
                    f"📦 **Mahsulot:** {product_name}\n"
                    f"📅 **Sana:** {order_date}\n"
                    f"────────────────────\n\n"
                )
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("✅ Kutayotgan buyurtmalar yo'q!")
    
    elif text == "💰 Kutayotgan To'lovlar":
        payments = db.get_pending_payments()
        if payments:
            message = "⏳ **Kutayotgan To'lovlar:**\n\n"
            for payment in payments[:10]:
                payment_id, user_name, phone, amount, payment_date, status, receipt_photo = payment
                message += (
                    f"🆔 **To'lov:** #{payment_id}\n"
                    f"👤 **Mijoz:** {user_name}\n"
                    f"📞 **Tel:** {phone}\n"
                    f"💰 **Summa:** {amount:,.0f} so'm\n"
                    f"📅 **Sana:** {payment_date}\n"
                    f"────────────────────\n\n"
                )
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("✅ Kutayotgan to'lovlar yo'q!")
    
    elif text == "✅ Buyurtmani Tasdiqlash":
        await update.message.reply_text(
            "🆔 **Tasdiqlash uchun buyurtma ID sini kiriting:**",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return CONFIRM_ORDER
    
    elif text == "❌ Buyurtmani Rad Etish":
        await update.message.reply_text(
            "🆔 **Rad etish uchun buyurtma ID sini kiriting:**",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return REJECT_ORDER  # ✅ Bu yerda REJECT_ORDER ga qaytishi kerak
    
    elif text == "✅ To'lovni Tasdiqlash":
        await update.message.reply_text(
            "🆔 **Tasdiqlash uchun to'lov ID sini kiriting:**",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return CONFIRM_PAYMENT
    
    elif text == "❌ To'lovni Rad Etish":
        await update.message.reply_text(
            "🆔 **Rad etish uchun to'lov ID sini kiriting:**",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return REJECT_PAYMENT  # ✅ Bu yerda REJECT_PAYMENT ga qaytishi kerak
    
    elif text == "⚠️ Sohta Chek Deb Belgilash":
        await update.message.reply_text(
            "🆔 **Sohta chek deb belgilash uchun to'lov ID sini kiriting:**",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return MARK_FAKE_PAYMENT
    
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "👨‍💼 **Admin Panel**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return ADMIN_MAIN
    
    return ORDER_MANAGEMENT

# Buyurtma tasdiqlash
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        order_id = int(update.message.text)
        
        # Buyurtma ma'lumotlarini olish
        order_info = db.get_order_by_id(order_id)
        if not order_info:
            await update.message.reply_text(
                f"❌ **Buyurtma #{order_id} topilmadi!**",
                reply_markup=get_order_management_keyboard()
            )
            return ORDER_MANAGEMENT
        
        success = db.update_order_status(order_id, 'completed')
        
        if success:
            # Foydalanuvchi ID sini olish
            user_id = order_info[1]  # order_info[1] - user_id maydoni
            
            # Foydalanuvchiga tasdiqlash xabarini yuboramiz
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 **BUYURTMANGIZ TASDIQLANDI!** 🎉\n\n"
                         "✅ **Buyurtmangiz muvaffaqiyatli tasdiqlandi!**\n"
                         "🚚 **Tez orada siz bilan etkazib berish xizmatchilarimiz bog'lanadi**\n"
                         "📞 **Iltimos, telefoningiz doim aloqada bo'lsin**\n\n"
                         "🕒 **Ish vaqti:** 09:00 - 18:00\n"
                         "👤 **Operator:** @Operator_Kino_1985\n"
                         "☎️ **Telefon:** +998(98)8882505"
                )
                logger.info(f"Foydalanuvchiga buyurtma tasdiqlash xabari yuborildi: user_id={user_id}")
            except Exception as e:
                logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                f"✅ **Buyurtma #{order_id} muvaffaqiyatli tasdiqlandi!**\n\n"
                f"Mijozga tasdiqlash haqida xabar yuborildi.",
                reply_markup=get_order_management_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ **Buyurtma #{order_id} topilmadi yoki tasdiqlanmadi!**",
                reply_markup=get_order_management_keyboard()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ **Noto'g'ri ID format!**\n\n"
            "Iltimos, faqat raqamlardan foydalaning.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return CONFIRM_ORDER
    
    return ORDER_MANAGEMENT

# To'lov tasdiqlash
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov tasdiqlash"""
    try:
        payment_id = int(update.message.text)
        
        # To'lov ma'lumotlarini olish
        payment_info = db.get_payment_by_id(payment_id)
        if not payment_info:
            await update.message.reply_text(
                f"❌ **To'lov #{payment_id} topilmadi!**",
                reply_markup=get_order_management_keyboard()
            )
            return ORDER_MANAGEMENT
        
        # To'lov statusini yangilash
        success = db.update_payment_status(payment_id, 'completed')
        
        if success:
            # Foydalanuvchi ID sini olish
            user_id = payment_info[1]  # payment_info[1] - user_id maydoni
            
            # Foydalanuvchiga tasdiqlash xabarini yuboramiz
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 **TO'LOVINGIZ TASDIQLANDI!** 🎉\n\n"
                         "✅ **To'lov muvaffaqiyatli tasdiqlandi!**\n"
                         "🚚 **Tez orada siz bilan etkazib berish xizmatchilarimiz bog'lanadi**\n"
                         "📞 **Iltimos, telefoningiz doim aloqada bo'lsin**\n\n"
                         "🕒 **Ish vaqti:** 09:00 - 18:00\n"
                         "👤 **Operator:** @Operator_Kino_1985\n"
                         "☎️ **Telefon:** +998(98)8882505"
                )
                logger.info(f"Foydalanuvchiga to'lov tasdiqlash xabari yuborildi: user_id={user_id}")
            except Exception as e:
                logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
                # Xabar yuborishda xatolik bo'lsa ham, adminga muvaffaqiyatli xabar yuboramiz
                await update.message.reply_text(
                    f"✅ **To'lov #{payment_id} muvaffaqiyatli tasdiqlandi!**\n\n"
                    f"⚠️ **Foydalanuvchiga xabar yuborishda xatolik:** {e}",
                    reply_markup=get_order_management_keyboard()
                )
                return ORDER_MANAGEMENT
            
            await update.message.reply_text(
                f"✅ **To'lov #{payment_id} muvaffaqiyatli tasdiqlandi!**\n\n"
                f"Mijozga tasdiqlash haqida xabar yuborildi.",
                reply_markup=get_order_management_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ **To'lov #{payment_id} topilmadi yoki tasdiqlanmadi!**",
                reply_markup=get_order_management_keyboard()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ **Noto'g'ri ID format!**\n\n"
            "Iltimos, faqat raqamlardan foydalaning.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return CONFIRM_PAYMENT
    
    return ORDER_MANAGEMENT
    
# admin.py faylida

async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buyurtmani rad etish (admin panel)"""
    try:
        order_id = int(update.message.text)
        success = db.update_order_status(order_id, 'rejected')
        
        if success:
            await update.message.reply_text(
                f"❌ **Buyurtma #{order_id} rad etildi!**",
                reply_markup=get_order_management_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ **Buyurtma #{order_id} topilmadi!**",
                reply_markup=get_order_management_keyboard()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ **Noto'g'ri ID format!**\n\n"
            "Iltimos, faqat raqamlardan foydalaning.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return REJECT_ORDER
    
    return ORDER_MANAGEMENT

async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lovni rad etish (admin panel)"""
    try:
        payment_id = int(update.message.text)
        success = db.update_payment_status(payment_id, 'rejected')
        
        if success:
            await update.message.reply_text(
                f"❌ **To'lov #{payment_id} rad etildi!**\n\n"
                f"✅ Mijozga rad etilganlik haqida xabar yuborildi.",
                reply_markup=get_order_management_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ **To'lov #{payment_id} topilmadi!**",
                reply_markup=get_order_management_keyboard()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ **Noto'g'ri ID format!**\n\n"
            "Iltimos, faqat raqamlardan foydalaning.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return REJECT_PAYMENT
    
    return ORDER_MANAGEMENT

async def mark_fake_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sohta chekni belgilash (admin panel)"""
    try:
        payment_id = int(update.message.text)
        success = db.update_payment_status(payment_id, 'fake')
        
        if success:
            # Foydalanuvchini bloklash
            payment_info = db.get_payment_by_id(payment_id)
            if payment_info:
                user_id = payment_info[1]
                db.block_user(user_id)
                
                # Bloklangan foydalanuvchiga xabar
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🚫 **SIZ BLOKLANDINGIZ!**\n\n"
                             "Sabab: Sohta to'lov cheki yuborish\n\n"
                             "📞 Blokdan ochish uchun admin bilan bog'lanin:\n"
                             "👤 @Operator_Kino_1985\n"
                             "☎️ +998(98)8882505"
                    )
                except Exception as e:
                    logger.error(f"Bloklangan foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                f"⚠️ **To'lov #{payment_id} sohta chek deb belgilandi!**\n\n"
                f"❌ Foydalanuvchi bloklandi va ogohlantirish xabari yuborildi.",
                reply_markup=get_order_management_keyboard()
            )
        else:
            await update.message.reply_text(
                f"❌ **To'lov #{payment_id} topilmadi!**",
                reply_markup=get_order_management_keyboard()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ **Noto'g'ri ID format!**\n\n"
            "Iltimos, faqat raqamlardan foydalaning.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return MARK_FAKE_PAYMENT
    
    return ORDER_MANAGEMENT   

# ==================== ADMIN ASOSIY MENYUSI ====================

# admin.py faylida admin_main funksiyasi ichida

async def admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    text = update.message.text
    
    # DEBUG: Nima yozayotganingizni ko'ramiz
    logger.info(f"Admin main: text='{text}', action={context.user_data.get('action')}")
    
    # 1. BEKOR QILISH tugmasi - birinchi tekshirish
    if text == "❌ Bekor qilish":
        context.user_data.clear()
        await update.message.reply_text(
            "✅ **Amal bekor qilindi!**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        return ADMIN_MAIN
    
    # 2. XABAR YUBORISH bosqichi
    elif context.user_data.get('action') == 'send_message_to_customer':
        target_user_id = context.user_data.get('contact_user_id')
        
        if not target_user_id:
            await update.message.reply_text(
                "❌ **Foydalanuvchi ID si topilmadi!**\n\n"
                "Qaytadan boshlang.",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            context.user_data.clear()
            return ADMIN_MAIN
        
        # Xabar uzunligini tekshirish
        if len(text.strip()) < 2:
            await update.message.reply_text(
                "❌ **Xabar juda qisqa!**\n\n"
                "Iltimos, kamida 2 belgidan iborat xabar yuboring.",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
        
        # Foydalanuvchiga xabar yuborish
        try:
            # Foydalanuvchi mavjudligini tekshirish
            user_info = db.get_user(target_user_id)
            if not user_info:
                await update.message.reply_text(
                    f"❌ **Foydalanuvchi topilmadi!**\n\n"
                    f"ID: `{target_user_id}`",
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
                context.user_data.clear()
                return ADMIN_MAIN
            
            # Xabar yuborish
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"📨 **Admin xabari:**\n\n{text}"
            )
            
            await update.message.reply_text(
                f"✅ **Xabar muvaffaqiyatli yuborildi!**\n\n"
                f"👤 **Foydalanuvchi ID:** `{target_user_id}`\n"
                f"📝 **Xabar:** {text}",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Admin xabar yubordi: admin_id={user_id}, target_id={target_user_id}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Xabar yuborishda xatolik: {error_msg}")
            
            await update.message.reply_text(
                f"❌ **Xabar yuborishda xatolik!**\n\n"
                f"👤 Foydalanuvchi ID: `{target_user_id}`\n\n"
                f"❌ **Xatolik:** {error_msg}\n\n"
                f"Foydalanuvchi botni bloklagan yoki mavjud emas.",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
        
        # User datani tozalash
        context.user_data.clear()
        return ADMIN_MAIN
    
    # 3. BROADCAST XABAR bosqichi
    elif context.user_data.get('action') == 'broadcast_message':
        # Bu yerda faqat context.user_data['broadcast_message'] ni saqlaymiz
        # Haqiqiy yuborish keyinroq
        context.user_data['broadcast_message'] = text
        
        # Tasdiqlash so'raymiz
        await update.message.reply_text(
            f"⚠️ **BARCHA FOYDALANUVCHILARGA XABAR YUBORISH** ⚠️\n\n"
            f"📝 **Xabar matni:**\n{text}\n\n"
            f"📊 **Foydalanuvchilar soni:** {len(db.get_all_users())} ta\n\n"
            f"❓ **Rostdan ham barcha foydalanuvchilarga shu xabarni yubormoqchimisiz?**",
            reply_markup=ReplyKeyboardMarkup([
                ["✅ HA, Yuborish", "❌ Yo'q, Bekor qilish"]
            ], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'confirm_broadcast'
        return ADMIN_MAIN
    
    # 4. BROADCAST TASDIQLASH
    elif context.user_data.get('action') == 'confirm_broadcast':
        if text == "✅ HA, Yuborish":
            message_text = context.user_data.get('broadcast_message', '')
            
            if not message_text:
                await update.message.reply_text(
                    "❌ **Xabar matni topilmadi!**",
                    reply_markup=get_admin_keyboard(),
                    parse_mode='Markdown'
                )
                context.user_data.clear()
                return ADMIN_MAIN
            
            # Xabarni yuborishni boshlaymiz
            await process_broadcast_message(update, context, message_text)
            
            # User datani tozalash
            context.user_data.clear()
            return ADMIN_MAIN
            
        elif text == "❌ Yo'q, Bekor qilish":
            await update.message.reply_text(
                "✅ **Xabar yuborish bekor qilindi!**",
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            context.user_data.clear()
            return ADMIN_MAIN
    
    # 5. ACTION handler (bloklash, bog'lanish)
    elif 'action' in context.user_data:
        action = context.user_data['action']
        
        # ID ni tekshirish
        try:
            target_user_id = int(text)
        except ValueError:
            await update.message.reply_text(
                "❌ **Iltimos, to'g'ri foydalanuvchi ID sini kiriting!**\n\n"
                "Faqat raqamlardan iborat bo'lishi kerak.\n"
                "Masalan: `8083596990`",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
        
        if action == 'block':
            await block_user_with_message(update, context, target_user_id)
            context.user_data.clear()
            return ADMIN_MAIN
        
        elif action == 'unblock':
            await unblock_user_with_message(update, context, target_user_id)
            context.user_data.clear()
            return ADMIN_MAIN
        
        elif action == 'contact_customer':
            # Mijoz bilan bog'lanish - ID ni saqlaymiz
            context.user_data['contact_user_id'] = target_user_id
            context.user_data['action'] = 'send_message_to_customer'
            
            await update.message.reply_text(
                f"👤 **Mijoz bilan bog'lanish**\n\n"
                f"✅ **Foydalanuvchi ID qabul qilindi:** `{target_user_id}`\n\n"
                f"📝 **Endi xabaringizni yuboring:**\n\n"
                f"Xabar yuborilgach, avtomatik admin panelga qaytasiz.\n"
                f"Bekor qilish uchun '❌ Bekor qilish' tugmasini bosing.",
                reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
            return ADMIN_MAIN
    
    # 6. Asosiy menyu tugmalari - BU YERGA QO'SHAMIZ! ⬇️
    elif text == "📦 Mahsulot Qo'shish":
        return await start_add_product(update, context)
    
    elif text == "🗑️ Mahsulot O'chirish":
        return await start_delete_product(update, context)
    
    elif text == "👥 Foydalanuvchilar":
        return await show_users_list(update, context)
    
    elif text == "📊 Statistika":
        total_users = len(db.get_all_users())
        total_products = len(db.get_all_products())
        total_orders = len(db.get_orders())
        
        motobike_products = len(db.get_products_by_category_only("🏍️ MotoBike"))
        scooter_products = len(db.get_products_by_category_only("🛵 Scooter"))
        electric_products = len(db.get_products_by_category_only("⚡ Electric Scooter"))
        
        stats_message = (
            "📊 **Bot Statistikasi**\n\n"
            f"👥 **Foydalanuvchilar:** {total_users} ta\n"
            f"📦 **Jami mahsulotlar:** {total_products} ta\n"
            f"📋 **Buyurtmalar:** {total_orders} ta\n\n"
            f"**Kategoriyalar bo'yicha:**\n"
            f"🏍️ **MotoBike:** {motobike_products} ta\n"
            f"🛵 **Scooter:** {scooter_products} ta\n"
            f"⚡ **Electric Scooter:** {electric_products} ta\n"
        )
        
        await update.message.reply_text(
            stats_message,
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    elif text == "🚫 Bloklash":
        await update.message.reply_text(
            "🚫 **Bloklash**\n\nFoydalanuvchi ID sini yuboring:\n\nMasalan: `8083596990`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'block'
    
    elif text == "✅ Blokdan Ochish":
        await update.message.reply_text(
            "✅ **Blokdan ochish**\n\nFoydalanuvchi ID sini yuboring:\n\nMasalan: `8083596990`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'unblock'
    
    elif text == "📋 Buyurtmalarni Boshqarish":
        await update.message.reply_text(
            "📋 **Buyurtma va To'lov Boshqaruvi**\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=get_order_management_keyboard(),
            parse_mode='Markdown'
        )
        return ORDER_MANAGEMENT
    
    elif text == "💰 To'lovlarni Boshqarish":
        await update.message.reply_text(
            "💰 **To'lov Boshqaruvi**\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=get_order_management_keyboard(),
            parse_mode='Markdown'
        )
        return ORDER_MANAGEMENT
    
    elif text == "📞 Foydalanuvchi bilan Bog'lanish":
        await update.message.reply_text(
            "👤 **Foydalanuvchi bilan bog'lanish**\n\n"
            "Foydalanuvchi ID sini kiriting:\n\n"
            "Masalan: `8083596990`",
            reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['action'] = 'contact_customer'
    
    # ✅ BU YERGA YANGI TUGMANI QO'SHAMIZ! ⬇️
    elif text == "📢 Xabar Yuborish":
        return await send_broadcast_message(update, context)
    
    elif text == "⬅️ Oldingi sahifa":
        page = context.user_data.get('users_page', 0)
        if page > 0:
            context.user_data['users_page'] = page - 1
            await show_users_page(update, context)
    
    elif text == "Keyingi sahifa ➡️":
        page = context.user_data.get('users_page', 0)
        total_pages = context.user_data.get('total_pages', 1)
        if page < total_pages - 1:
            context.user_data['users_page'] = page + 1
            await show_users_page(update, context)
    
    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "👨‍💼 **Admin Panel**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    elif text == "🔴 Admin Paneldan Chiqish":
        await update.message.reply_text(
            "👋 **Admin paneldan chiqdingiz!**\n\n"
            "Qaytish uchun /admin yoki /start buyrug'ini yuboring.",
            reply_markup=ReplyKeyboardMarkup([["/start"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # Agar boshqa narsa yozilsa
    else:
        await update.message.reply_text(
            "🤔 **Noma'lum buyruq!**\n\n"
            "Iltimos, menyudan tugmalardan birini tanlang.",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
    
    return ADMIN_MAIN

# Foydalanuvchilar sahifasini ko'rsatish
async def show_users_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    page = context.user_data.get('users_page', 0)
    users_per_page = 5
    total_pages = (len(users) + users_per_page - 1) // users_per_page
    
    start_idx = page * users_per_page
    end_idx = start_idx + users_per_page
    current_users = users[start_idx:end_idx]
    
    message = f"👥 **Barcha foydalanuvchilar** ({len(users)} ta)\n\n"
    message += f"📄 **Sahifa:** {page + 1}/{total_pages}\n\n"
    
    for user in current_users:
        if len(user) >= 8:
            user_id, first_name, phone, location, language, registered, reg_date, blocked = user
        else:
            continue
        
        status = "✅ Faol" if not blocked else "🚫 Bloklangan"
        reg_status = "✅ Ro'yxatdan o'tgan" if registered else "❌ Ro'yxatdan o'tmagan"
        phone_display = phone if phone else "❌ Ko'rsatilmagan"
        location_display = location if location else "❌ Ko'rsatilmagan"
        
        message += (
            f"🆔 **ID:** `{user_id}`\n"
            f"👤 **Ism:** {first_name}\n"
            f"📞 **Tel:** {phone_display}\n"
            f"📍 **Manzil:** {location_display}\n"
            f"🌐 **Til:** {language}\n"
            f"📅 **Ro'yxatdan o'tgan:** {reg_date}\n"
            f"🔰 **Holat:** {status}\n"
            f"📋 **Ro'yxat:** {reg_status}\n"
            f"────────────────────\n\n"
        )
    
    # Yangi keyboard qurilishi
    keyboard = []
    
    # Sahifalash tugmalari
    if page > 0:
        keyboard.append(["⬅️ Oldingi sahifa"])
    
    if page < total_pages - 1:
        keyboard.append(["Keyingi sahifa ➡️"])
    
    # BOG'LANISH tugmasi
    keyboard.append(["📞 Foydalanuvchi bilan Bog'lanish"])
    keyboard.append(["🔙 Orqaga"])
    
    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def show_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchilar ro'yxatini ko'rsatish"""
    users = db.get_all_users()
    
    # Sahifalashni boshlash
    context.user_data['users_page'] = 0
    
    if users:
        page = 0
        users_per_page = 5
        total_pages = (len(users) + users_per_page - 1) // users_per_page
        
        start_idx = page * users_per_page
        end_idx = start_idx + users_per_page
        current_users = users[start_idx:end_idx]
        
        message = f"👥 **Barcha foydalanuvchilar** ({len(users)} ta)\n\n"
        message += f"📄 **Sahifa:** {page + 1}/{total_pages}\n\n"
        
        for user in current_users:
            if len(user) >= 8:
                user_id, first_name, phone, location, language, registered, reg_date, blocked = user
            else:
                continue
            
            status = "✅ Faol" if not blocked else "🚫 Bloklangan"
            reg_status = "✅ Ro'yxatdan o'tgan" if registered else "❌ Ro'yxatdan o'tmagan"
            phone_display = phone if phone else "❌ Ko'rsatilmagan"
            location_display = location if location else "❌ Ko'rsatilmagan"
            
            message += (
                f"🆔 **ID:** `{user_id}`\n"
                f"👤 **Ism:** {first_name}\n"
                f"📞 **Tel:** {phone_display}\n"
                f"📍 **Manzil:** {location_display}\n"
                f"🌐 **Til:** {language}\n"
                f"📅 **Ro'yxatdan o'tgan:** {reg_date}\n"
                f"🔰 **Holat:** {status}\n"
                f"📋 **Ro'yxat:** {reg_status}\n"
                f"────────────────────\n\n"
            )
        
        # Keyboard yaratish
        keyboard = []
        
        if total_pages > 1 and page < total_pages - 1:
            keyboard.append(["Keyingi sahifa ➡️"])
        
        keyboard.append(["📞 Foydalanuvchi bilan Bog'lanish"])
        keyboard.append(["🔙 Orqaga"])
        
        context.user_data['total_pages'] = total_pages
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ **Foydalanuvchilar topilmadi!**",
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )
        
# Xabar yuborish tugmasini qo'shish
async def send_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha foydalanuvchilarga xabar yuborish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    context.user_data['action'] = 'broadcast_message'
    
    await update.message.reply_text(
        "📢 **Barcha foydalanuvchilarga xabar yuborish**\n\n"
        "Xabar matnini kiriting:\n\n"
        "❗ **Diqqat:** Bu xabar BARCHA foydalanuvchilarga yuboriladi!",
        reply_markup=ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True),
        parse_mode='Markdown'
    )
    return ADMIN_MAIN      

# admin.py faylida yangi funksiya:
async def process_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text):
    """Barcha foydalanuvchilarga xabar yuborish"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    # Barcha foydalanuvchilarni olish
    all_users = db.get_all_users()
    total_users = len(all_users)
    successful = 0
    failed = 0
    
    # Progress xabari
    progress_msg = await update.message.reply_text(
        f"📤 **Xabar yuborilmoqda...**\n\n"
        f"📊 Jami foydalanuvchilar: {total_users}\n"
        f"✅ Muvaffaqiyatli: 0\n"
        f"❌ Xatolik: 0"
    )
    
    # Har bir foydalanuvchiga xabar yuborish
    for i, user in enumerate(all_users):
        try:
            target_user_id = user[0]  # user_id maydoni
            
            # Xabarni yuborish
            await context.bot.send_message(
                chat_id=target_user_id,
                text=message_text,
                parse_mode='Markdown'
            )
            successful += 1
            
            # Har 10 ta xabardan keyin progress yangilash
            if (i + 1) % 10 == 0 or (i + 1) == total_users:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=progress_msg.message_id,
                    text=f"📤 **Xabar yuborilmoqda...**\n\n"
                         f"📊 Jami foydalanuvchilar: {total_users}\n"
                         f"📨 Yuborildi: {i + 1}/{total_users}\n"
                         f"✅ Muvaffaqiyatli: {successful}\n"
                         f"❌ Xatolik: {failed}"
                )
                await asyncio.sleep(0.5)  # Rate limit uchun
        
        except Exception as e:
            failed += 1
            logger.error(f"Xabar yuborishda xatolik user_id={target_user_id}: {e}")
    
    # Yakuniy xabar
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=progress_msg.message_id,
        text=f"✅ **Xabar yuborish yakunlandi!**\n\n"
             f"📊 Jami foydalanuvchilar: {total_users}\n"
             f"✅ Muvaffaqiyatli: {successful}\n"
             f"❌ Xatolik: {failed}\n\n"
             f"📈 Muvaffaqiyat: {successful/total_users*100:.1f}%"
    )
    
    # Admin panelga qaytish
    await update.message.reply_text(
        "👨‍💼 **Admin Panel**",
        reply_markup=get_admin_keyboard(),
        parse_mode='Markdown'
    ) 

# admin.py ga yangi funksiyalar:
async def messenger_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-messenger boshqaruvi"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🤖 **Avtomatik Xabar Yuborish Tizimi**\n\n"
        "📅 **Jadval:** Kuniga 3 marta\n"
        "🕗 **08:00** - Ertalabki salom\n"
        "🕑 **14:00** - Tushki xabar\n"
        "🕗 **20:00** - Kechki xabar\n\n"
        "👥 **Kimlarga:** Barcha ro'yxatdan o'tgan foydalanuvchilar\n"
        "📍 **Vaqt:** Toshkent (GMT+5)\n\n"
        "Boshqaruvni tanlang:",
        reply_markup=ReplyKeyboardMarkup([
            ["▶️ Messenger ni Yoqish", "⏸️ Messenger ni To'xtatish"],
            ["📤 Test Xabarni Yuborish", "📊 Holatni Ko'rish"],
            ["🔙 Orqaga"]
        ], resize_keyboard=True),
        parse_mode='Markdown'
    )
    return ADMIN_MAIN

elif text == "🤖 Avtomatik Xabarlar":
    return await yearly_messenger_control(update, context)  

# admin.py ga:
async def yearly_messenger_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yearly messenger boshqaruv"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END
    
    # Messenger holati
    status = "✅ Ishlamoqda" if yearly_messenger and yearly_messenger.running else "❌ To'xtatilgan"
    
    # Joriy va kelgusi oylar
    if yearly_messenger:
        year, month = yearly_messenger.get_current_month_year()
        current_month = f"{year}-{month}"
    else:
        current_month = "Noma'lum"
    
    await update.message.reply_text(
        f"🗓️ <b>2025-2026 Yillik Avtomatik Xabar Yuborish</b>\n\n"
        f"📅 <b>Davr:</b> 2025 Dekabr - 2026 Dekabr\n"
        f"📆 <b>Joriy oy:</b> {current_month}\n"
        f"⏰ <b>Vaqt:</b> Toshkent (GMT+5)\n\n"
        f"🔄 <b>Holat:</b> {status}\n"
        f"⏳ <b>Kunlik xabarlar:</b>\n"
        f"• ☀️ 08:00 - Ertalabki\n"
        f"• 🕑 14:00 - Tushki\n"
        f"• 🌙 20:00 - Kechki\n\n"
        f"🌍 <b>Tillar:</b> 🇺🇿 O'zbek, 🇷🇺 Русский, 🇺🇸 English\n\n"
        f"🎯 <b>Oylik mavzular:</b>\n"
        f"• Dekabr - Yangi yil tayyorgarligi\n"
        f"• Yanvar - Yangi imkoniyatlar\n"
        f"• Fevral - Sevgililar kuni\n"
        f"• Mart - Bahor, Navro'z\n"
        f"• ... va boshqalar\n\n"
        f"<i>📊 Har oy uchun maxsus xabarlar mavjud</i>",
        reply_markup=ReplyKeyboardMarkup([
            ["▶️ Yoqish", "⏸️ To'xtatish"],
            ["📤 Bugungi Test", "📅 Oyni Ko'rish"],
            ["🔄 Vaqtni Tekshirish", "📊 Statistika"],
            ["🔙 Orqaga"]
        ], resize_keyboard=True),
        parse_mode='HTML'
    )
    return ADMIN_MAIN 

# Admin handlerini qaytarish funksiyasi
def get_admin_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('admin', admin_start)],
        states={
            ADMIN_MAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_main)],
            ADD_PRODUCT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_category)],
            ADD_PRODUCT_SUBCATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_subcategory)],
            ADD_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_name)],
            ADD_PRODUCT_PRICE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_currency)],
            ADD_PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_price)],
            ADD_PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_description)],
            ADD_PRODUCT_PHOTOS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_photos),
                MessageHandler(filters.PHOTO, get_product_photos)
            ],
            DELETE_PRODUCT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_delete_category)],
            DELETE_PRODUCT_SELECT: [
                MessageHandler(filters.Regex("^(⬅️ Oldingi sahifa|Keyingi sahifa ➡️|🗑️ Mahsulotni O'chirish|🔙 Orqaga)$"), delete_product_pagination),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_id_for_deletion)
            ],
            DELETE_PRODUCT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_product_deletion)],
            ORDER_MANAGEMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_management)
            ],
            CONFIRM_ORDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)
            ],
            REJECT_ORDER: [  # ✅ YANGI: reject_order uchun handler
                MessageHandler(filters.TEXT & ~filters.COMMAND, reject_order)
            ],
            CONFIRM_PAYMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_payment)
            ],
            REJECT_PAYMENT: [  # ✅ YANGI: reject_payment uchun handler
                MessageHandler(filters.TEXT & ~filters.COMMAND, reject_payment)
            ],
            MARK_FAKE_PAYMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, mark_fake_payment)
            ]
        },
        fallbacks=[
            CommandHandler('admin', admin_start),
            CommandHandler('start', admin_start)  # Admin uchun start ham admin panelga olib boradi
        ],
        allow_reentry=True,
        name="admin_conversation"
    )