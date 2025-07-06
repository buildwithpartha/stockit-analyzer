#!/usr/bin/env python3
"""
Debug Environment Variables
Helps debug environment variable configuration
"""

import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_environment():
    """Debug environment variables"""
    logger.info("=== Environment Variables Debug ===")
    
    # Load .env file
    env_loaded = load_dotenv()
    logger.info(f"✅ .env file loaded: {env_loaded}")
    
    # Check all relevant environment variables
    env_vars = {
        'NEWS_API_KEY': 'News API Key',
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID', 
        'TWILIO_AUTH_TOKEN': 'Twilio Auth Token',
        'TWILIO_FROM_NUMBER': 'Twilio From Number',
        'TWILIO_TO_NUMBER': 'Twilio To Number',
        'USE_WHATSAPP': 'Use WhatsApp',
        'WHATSAPP_FROM_NUMBER': 'WhatsApp From Number',
        'SMS_ALERT_TIME': 'SMS Alert Time',
        'SMS_ALERT_TIMEZONE': 'SMS Alert Timezone'
    }
    
    logger.info("\nEnvironment Variables Status:")
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            # Hide sensitive information
            if var in ['NEWS_API_KEY', 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']:
                display_value = f"{'*' * len(value)} (length: {len(value)})"
            else:
                display_value = value
            logger.info(f"✅ {description} ({var}): {display_value}")
        else:
            logger.warning(f"❌ {description} ({var}): Not set")
    
    # Check .env file existence and content
    if os.path.exists('.env'):
        logger.info("\n✅ .env file exists")
        try:
            with open('.env', 'r') as f:
                lines = f.readlines()
            logger.info(f"📄 .env file has {len(lines)} lines")
            
            # Show non-sensitive lines
            logger.info("\n.env file content (sensitive values hidden):")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if any(sensitive in line for sensitive in ['API_KEY', 'TOKEN', 'SID']):
                        key = line.split('=')[0] if '=' in line else line
                        logger.info(f"{i:2d}: {key}=*** (hidden)")
                    else:
                        logger.info(f"{i:2d}: {line}")
                elif line.startswith('#'):
                    logger.info(f"{i:2d}: {line}")
                    
        except Exception as e:
            logger.error(f"❌ Error reading .env file: {str(e)}")
    else:
        logger.error("❌ .env file not found")
    
    # Check SSL environment variables
    ssl_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
    logger.info("\nSSL Environment Variables:")
    for var in ssl_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: {value}")
        else:
            logger.info(f"❌ {var}: Not set")

def check_file_permissions():
    """Check file permissions"""
    logger.info("\n=== File Permissions Check ===")
    
    files_to_check = ['.env', 'input.txt', 'requirements.txt']
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                # Check if file is readable
                with open(filename, 'r') as f:
                    f.read(1)  # Try to read one character
                logger.info(f"✅ {filename}: Readable")
            except Exception as e:
                logger.error(f"❌ {filename}: Read error - {str(e)}")
        else:
            logger.warning(f"⚠️ {filename}: File not found")

def check_python_modules():
    """Check if required Python modules are available"""
    logger.info("\n=== Python Modules Check ===")
    
    required_modules = [
        'streamlit', 'pandas', 'yfinance', 'plotly', 'twilio',
        'python-dotenv', 'schedule', 'ta', 'requests', 'certifi',
        'numpy', 'pytz', 'logging'
    ]
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            logger.info(f"✅ {module}: Available")
        except ImportError:
            logger.error(f"❌ {module}: Not available")

def main():
    """Main debug function"""
    logger.info("Starting Environment Debug...")
    
    debug_environment()
    check_file_permissions()
    check_python_modules()
    
    logger.info("\n=== Debug Summary ===")
    logger.info("If you see any ❌ errors above, please fix them before running the application.")
    logger.info("For missing modules, run: pip install -r requirements.txt")
    logger.info("For missing .env variables, check the .env file and add missing values.")

if __name__ == "__main__":
    main()
