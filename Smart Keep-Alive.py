def smart_keep_alive():
    """Aqlli keep-alive - turli intervalda turli endpointlar"""
    counter = 0
    while True:
        try:
            counter += 1
            
            # HAR 1-CHI: Asosiy sahifa
            if counter % 1 == 0:
                requests.get('https://moto-bike-jliv.onrender.com/', timeout=5)
                logger.info("✅ Main page ping")
            
            # HAR 2-CHI: Ping
            if counter % 2 == 0:
                requests.get('https://moto-bike-jliv.onrender.com/ping', timeout=5)
                logger.info("✅ Ping endpoint")
            
            # HAR 3-CHI: Status
            if counter % 3 == 0:
                requests.get('https://moto-bike-jliv.onrender.com/status', timeout=5)
                logger.info("✅ Status check")
            
            # HAR 6-CHI: Batafsil monitoring
            if counter % 6 == 0:
                requests.get('https://moto-bike-jliv.onrender.com/monitoring', timeout=5)
                logger.info("✅ Full monitoring")
            
            # Counter ni qayta nol qilish
            if counter >= 6:
                counter = 0
                
        except Exception as e:
            logger.error(f"❌ Smart keep-alive: {e}")
        
        # HAR 60 SONIYADA BIR
        time.sleep(60)