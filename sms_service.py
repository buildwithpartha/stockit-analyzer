import os
import logging
from datetime import datetime
import pytz
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
import requests
import schedule
import time
import threading
from dotenv import load_dotenv
import ssl
import certifi

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomTwilioHttpClient(TwilioHttpClient):
    """Custom Twilio HTTP client with SSL certificate handling"""
    
    def request(self, method, url, params=None, data=None, headers=None, auth=None, timeout=None, allow_redirects=False):
        """Override request method to handle SSL certificates"""
        try:
            # Try with SSL verification first
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                auth=auth,
                timeout=timeout,
                allow_redirects=allow_redirects,
                verify=certifi.where()  # Use certifi for SSL verification
            )
            return response
        except Exception as e:
            logger.warning(f"SSL verification failed, trying without verification: {str(e)}")
            # Fallback: disable SSL verification
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                auth=auth,
                timeout=timeout,
                allow_redirects=allow_redirects,
                verify=False
            )
            return response

class SMSService:
    def __init__(self):
        # Try to get from Streamlit secrets first (for Streamlit Cloud), then environment variables
        self.account_sid = self._get_config('TWILIO_ACCOUNT_SID')
        self.auth_token = self._get_config('TWILIO_AUTH_TOKEN')
        self.from_number = self._get_config('TWILIO_FROM_NUMBER')
        self.to_number = self._get_config('TWILIO_TO_NUMBER')
        self.sms_enabled = self._get_bool_config('SMS_ENABLED', False)
        self.use_whatsapp = self._get_bool_config('USE_WHATSAPP', False)
        self.whatsapp_from = self._get_config('WHATSAPP_FROM_NUMBER', 'whatsapp:+14155238886')
        self.alert_time = self._get_config('SMS_ALERT_TIME', '08:00')
        self.timezone = self._get_config('SMS_ALERT_TIMEZONE', 'Asia/Kolkata')
        
        # Initialize Twilio client with custom HTTP client
        if self.account_sid and self.auth_token:
            try:
                http_client = CustomTwilioHttpClient()
                self.client = Client(self.account_sid, self.auth_token, http_client=http_client)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None
        else:
            logger.warning("Twilio credentials not found")
            self.client = None
            
        self.scheduler_running = False
        self.scheduler_thread = None
    
    def _get_config(self, key, default=None):
        """Get configuration from Streamlit secrets or environment variables"""
        try:
            # Try Streamlit secrets first (if running in Streamlit)
            import streamlit as st
            return st.secrets.get(key, os.getenv(key, default))
        except:
            # Fallback to environment variables
            return os.getenv(key, default)
    
    def _get_bool_config(self, key, default=False):
        """Get boolean configuration from Streamlit secrets or environment variables"""
        try:
            # Try Streamlit secrets first (if running in Streamlit)
            import streamlit as st
            value = st.secrets.get(key, os.getenv(key, str(default)))
        except:
            # Fallback to environment variables
            value = os.getenv(key, str(default))
        
        # Handle different boolean representations
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        else:
            return bool(value)
    
    def send_whatsapp_message(self, message):
        """Send WhatsApp message with fallback to SMS if needed"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
            
        if not self.use_whatsapp:
            logger.info("WhatsApp disabled, trying SMS")
            return self.send_sms_message(message) if self.sms_enabled else False
            
        try:
            whatsapp_to = f"whatsapp:{self.to_number}"
            
            # Send WhatsApp message
            message_obj = self.client.messages.create(
                body=message,
                from_=self.whatsapp_from,
                to=whatsapp_to
            )
            logger.info(f"WhatsApp message sent successfully: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp message failed: {str(e)}")
            
            # Fallback to SMS only if SMS is enabled
            if self.sms_enabled:
                logger.info("Falling back to SMS")
                return self.send_sms_message(message)
            else:
                logger.info("SMS disabled, no fallback available")
                return False
    
    def send_sms_message(self, message):
        """Send SMS message"""
        if not self.sms_enabled:
            logger.info("SMS disabled, not sending SMS")
            return False
            
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
            
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            logger.info(f"SMS sent successfully: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def format_stock_message(self, stock_data):
        """Format stock data into a message"""
        try:
            symbol = stock_data['symbol'].replace('.NS', '')
            recommendation = stock_data['recommendation']
            current_price = stock_data['current_price']
            target_price = stock_data['target_price']
            potential_return = stock_data['potential_return']
            confidence = stock_data['confidence']
            overall_score = stock_data['overall_score']
            divergence_signal = stock_data['divergence_signal']
            tradingview_link = stock_data['tradingview_link']
            
            # Emoji mapping for recommendations
            emoji_map = {
                'STRONG_BUY': '🚀',
                'BUY': '📈',
                'HOLD': '⏸️',
                'SELL': '📉',
                'STRONG_SELL': '🔻'
            }
            
            emoji = emoji_map.get(recommendation, '➡️')
            
            message = f"""{emoji} {symbol} - {recommendation}
LTP: ₹{current_price}
Target: ₹{target_price}
Potential: {potential_return}%
Confidence: {confidence}%
Score: {overall_score}/100
Signal: {divergence_signal}
TradingView: {tradingview_link}"""
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting stock message: {str(e)}")
            return f"Error formatting message for {stock_data.get('symbol', 'Unknown')}"
    
    def send_analysis_alerts(self, analysis_results):
        """Send consolidated alert for analysis results"""
        if not analysis_results:
            logger.info("No analysis results to send")
            return
            
        try:
            # Filter for actionable recommendations (STRONG_BUY, BUY, STRONG_SELL only)
            actionable_stocks = [
                stock for stock in analysis_results 
                if stock['recommendation'] in ['STRONG_BUY', 'BUY', 'STRONG_SELL']
            ]
            
            if not actionable_stocks:
                logger.info("No actionable stocks found")
                return
                
            # Create consolidated message
            message = self.create_consolidated_alert(actionable_stocks)
            
            # Send single WhatsApp message
            success = self.send_whatsapp_message(message)
            
            if success:
                logger.info(f"Consolidated alert sent for {len(actionable_stocks)} stocks")
            else:
                logger.error("Failed to send consolidated alert")
                
        except Exception as e:
            logger.error(f"Error sending analysis alerts: {str(e)}")
    
    def create_consolidated_alert(self, stocks):
        """Create a single consolidated message for all actionable stocks"""
        try:
            # Sort stocks by recommendation priority
            strong_buys = [s for s in stocks if s['recommendation'] == 'STRONG_BUY']
            buys = [s for s in stocks if s['recommendation'] == 'BUY']
            strong_sells = [s for s in stocks if s['recommendation'] == 'STRONG_SELL']
            
            # Sort by score within each category
            strong_buys.sort(key=lambda x: x['overall_score'], reverse=True)
            buys.sort(key=lambda x: x['overall_score'], reverse=True)
            strong_sells.sort(key=lambda x: x['overall_score'])
            
            message_parts = ["📈 Indian Stock Alert"]
            
            # Add STRONG_BUY stocks
            if strong_buys:
                message_parts.append("\n🚀 STRONG BUY:")
                for stock in strong_buys[:3]:  # Top 3
                    symbol = stock['symbol'].replace('.NS', '')
                    message_parts.append(f"• {symbol}: ₹{stock['current_price']} → ₹{stock['target_price']} ({stock['potential_return']:+.1f}%)")
            
            # Add BUY stocks
            if buys:
                message_parts.append("\n📈 BUY:")
                for stock in buys[:3]:  # Top 3
                    symbol = stock['symbol'].replace('.NS', '')
                    message_parts.append(f"• {symbol}: ₹{stock['current_price']} → ₹{stock['target_price']} ({stock['potential_return']:+.1f}%)")
            
            # Add STRONG_SELL stocks
            if strong_sells:
                message_parts.append("\n🔻 STRONG SELL:")
                for stock in strong_sells[:2]:  # Top 2
                    symbol = stock['symbol'].replace('.NS', '')
                    message_parts.append(f"• {symbol}: ₹{stock['current_price']} → ₹{stock['target_price']} ({stock['potential_return']:+.1f}%)")
            
            message_parts.append(f"\nTotal: {len(stocks)} actionable stocks")
            message_parts.append("⚠️ Not investment advice")
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"Error creating consolidated alert: {str(e)}")
            return "📈 Stock Alert - Error creating message"
                
        except Exception as e:
            logger.error(f"Error sending analysis alerts: {str(e)}")
    
    def send_manual_alert(self, message):
        """Send manual alert message"""
        return self.send_whatsapp_message(message)
    
    def test_connection(self):
        """Test SMS/WhatsApp connection"""
        test_message = "🧪 Test message from Indian Stock Market Analyzer"
        
        if not self.client:
            return False, "Twilio client not initialized"
            
        try:
            success = self.send_whatsapp_message(test_message)
            if success:
                return True, "Test message sent successfully"
            else:
                return False, "Failed to send test message"
        except Exception as e:
            return False, f"Test failed: {str(e)}"
    
    def start_scheduler(self, analysis_callback):
        """Start the scheduled alert system"""
        if self.scheduler_running:
            logger.info("Scheduler already running")
            return
            
        def run_scheduler():
            schedule.every().day.at(self.alert_time).do(self._scheduled_alert, analysis_callback)
            logger.info(f"Scheduler started - alerts at {self.alert_time} {self.timezone}")
            
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("SMS scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduled alert system"""
        self.scheduler_running = False
        schedule.clear()
        logger.info("SMS scheduler stopped")
    
    def _scheduled_alert(self, analysis_callback):
        """Internal method for scheduled alerts"""
        try:
            logger.info("Running scheduled analysis for alerts")
            
            # Get current analysis results
            analysis_results = analysis_callback()
            
            if analysis_results:
                # Send summary message first
                summary_message = self._create_summary_message(analysis_results)
                self.send_whatsapp_message(summary_message)
                
                # Send individual alerts
                self.send_analysis_alerts(analysis_results)
            else:
                logger.warning("No analysis results available for scheduled alert")
                
        except Exception as e:
            logger.error(f"Error in scheduled alert: {str(e)}")
    
    def _create_summary_message(self, analysis_results):
        """Create summary message for daily alerts"""
        try:
            total_stocks = len(analysis_results)
            
            # Count recommendations
            rec_counts = {}
            for stock in analysis_results:
                rec = stock['recommendation']
                rec_counts[rec] = rec_counts.get(rec, 0) + 1
            
            current_time = datetime.now(pytz.timezone(self.timezone)).strftime("%Y-%m-%d %H:%M")
            
            summary = f"""📊 Daily Stock Analysis Summary
Time: {current_time}
Total Stocks: {total_stocks}

🚀 Strong Buy: {rec_counts.get('STRONG_BUY', 0)}
📈 Buy: {rec_counts.get('BUY', 0)}
⏸️ Hold: {rec_counts.get('HOLD', 0)}
📉 Sell: {rec_counts.get('SELL', 0)}
🔻 Strong Sell: {rec_counts.get('STRONG_SELL', 0)}

Top alerts will follow..."""
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating summary message: {str(e)}")
            return "📊 Daily Stock Analysis Summary - Error generating summary"
    
    def get_status(self):
        """Get service status"""
        status = {
            'client_initialized': self.client is not None,
            'scheduler_running': self.scheduler_running,
            'sms_enabled': self.sms_enabled,
            'whatsapp_enabled': self.use_whatsapp,
            'alert_time': self.alert_time,
            'timezone': self.timezone
        }
        return status
    
    def send_whatsapp_simple_alert(self, stock_symbol, recommendation, price):
        """Send simplified WhatsApp alert that's more likely to work in sandbox"""
        if not self.client or not self.use_whatsapp:
            return False
            
        try:
            # Create a very simple message format
            simple_message = f"{stock_symbol}: {recommendation} @ ₹{price}"
            
            whatsapp_to = f"whatsapp:{self.to_number}"
            message_obj = self.client.messages.create(
                body=simple_message,
                from_=self.whatsapp_from,
                to=whatsapp_to
            )
            logger.info(f"WhatsApp simple alert sent: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp simple alert failed: {str(e)}")
            return False
