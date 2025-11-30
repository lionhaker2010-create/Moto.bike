# main() funksiyasini yangilang
def main():
    # Flask server
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    logger.info("✅ Flask server started")
    
    # Keep-alive - TEZLASHTIRDIK
    threading.Thread(target=keep_awake, daemon=True).start()
    logger.info("✅ Keep-alive started")
    
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("BOT_TOKEN topilmadi!")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    # Handlerlarni qo'shish
    from admin import get_admin_handler
    application.add_handler(get_admin_handler())
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(conv_handler)
    
    logger.info("Bot ishga tushdi!")
    
    # ✅ YANGILANGAN POLLING
    application.run_polling(
        poll_interval=1.0,
        timeout=10,
        drop_pending_updates=True,
        allowed_updates=['message', 'callback_query']
    )