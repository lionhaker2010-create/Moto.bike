import os
import time
import logging

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_bot():
    """Botni ishga tushirish"""
    try:
        from main import main
        main()
    except Exception as e:
        logger.error(f"Bot ishga tushmadi: {e}")
        time.sleep(10)
        run_bot()  # Qayta urinish

if __name__ == '__main__':
    logger.info("🚀 Bot ishga tushmoqda...")
    run_bot()