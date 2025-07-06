#!/usr/bin/env python3
"""
SMS Scheduler Runner
Standalone script to run SMS alerts scheduler
"""

import logging
import time
from stock_analyzer import StockAnalyzer
from sms_service import SMSService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_stock_symbols():
    """Load stock symbols from input.txt"""
    try:
        with open('input.txt', 'r') as f:
            content = f.read()
        symbols = [symbol.strip() for symbol in content.replace('\n', ',').split(',') if symbol.strip()]
        return symbols
    except FileNotFoundError:
        logger.error("input.txt file not found")
        return []

def analyze_stocks_for_alerts():
    """Analyze stocks and return results for alerts"""
    try:
        symbols = load_stock_symbols()
        if not symbols:
            logger.error("No stock symbols loaded")
            return []
        
        analyzer = StockAnalyzer()
        logger.info(f"Analyzing {len(symbols)} stocks for alerts...")
        
        results = analyzer.analyze_stocks(symbols)
        logger.info(f"Analysis completed. {len(results)} stocks analyzed.")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in stock analysis: {str(e)}")
        return []

def main():
    """Main function to run SMS scheduler"""
    logger.info("Starting SMS Scheduler...")
    
    try:
        # Initialize SMS service
        sms_service = SMSService()
        
        # Check if service is properly configured
        status = sms_service.get_status()
        if not status['client_initialized']:
            logger.error("SMS service not properly configured. Check your .env file.")
            return
        
        logger.info("SMS service initialized successfully")
        logger.info(f"Alert time: {status['alert_time']} {status['timezone']}")
        logger.info(f"WhatsApp: {'Enabled' if status['whatsapp_enabled'] else 'Disabled'}")
        
        # Start scheduler with analysis callback
        sms_service.start_scheduler(analyze_stocks_for_alerts)
        
        logger.info("SMS Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping SMS Scheduler...")
            sms_service.stop_scheduler()
            logger.info("SMS Scheduler stopped.")
            
    except Exception as e:
        logger.error(f"Error running SMS scheduler: {str(e)}")

if __name__ == "__main__":
    main()
