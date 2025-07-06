#!/usr/bin/env python3
"""
SSL Certificate Fix Script for Indian Stock Market Analyzer
This script helps resolve SSL certificate issues commonly encountered on macOS
"""

import os
import ssl
import certifi
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_ssl_certificates():
    """Fix SSL certificate issues"""
    try:
        # Get the path to certifi certificates
        cert_path = certifi.where()
        logger.info(f"Certifi certificate path: {cert_path}")
        
        # Set SSL environment variables
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['SSL_CERT_DIR'] = os.path.dirname(cert_path)
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['CURL_CA_BUNDLE'] = cert_path
        
        logger.info("SSL environment variables set:")
        logger.info(f"SSL_CERT_FILE: {os.environ.get('SSL_CERT_FILE')}")
        logger.info(f"SSL_CERT_DIR: {os.environ.get('SSL_CERT_DIR')}")
        logger.info(f"REQUESTS_CA_BUNDLE: {os.environ.get('REQUESTS_CA_BUNDLE')}")
        
        # Test SSL connection
        test_ssl_connection()
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing SSL certificates: {str(e)}")
        return False

def test_ssl_connection():
    """Test SSL connection to common endpoints"""
    test_urls = [
        'https://api.twilio.com',
        'https://query1.finance.yahoo.com',
        'https://httpbin.org/get'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10, verify=certifi.where())
            logger.info(f"✅ SSL test successful for {url} - Status: {response.status_code}")
        except requests.exceptions.SSLError as e:
            logger.warning(f"❌ SSL test failed for {url}: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Connection test failed for {url}: {str(e)}")
        except Exception as e:
            logger.warning(f"⚠️ Unexpected error testing {url}: {str(e)}")

def create_ssl_context():
    """Create a custom SSL context"""
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        logger.info("Custom SSL context created")
        return context
    except Exception as e:
        logger.error(f"Error creating SSL context: {str(e)}")
        return None

def print_ssl_info():
    """Print SSL configuration information"""
    logger.info("=== SSL Configuration Information ===")
    logger.info(f"Python SSL version: {ssl.OPENSSL_VERSION}")
    logger.info(f"Certifi version: {certifi.__version__}")
    logger.info(f"Certifi certificate file: {certifi.where()}")
    logger.info(f"Default SSL context: {ssl.create_default_context()}")
    
    # Check if certificate file exists
    cert_file = certifi.where()
    if os.path.exists(cert_file):
        file_size = os.path.getsize(cert_file)
        logger.info(f"Certificate file exists: {cert_file} ({file_size} bytes)")
    else:
        logger.error(f"Certificate file not found: {cert_file}")

def main():
    """Main function"""
    logger.info("Starting SSL Certificate Fix...")
    
    print_ssl_info()
    
    success = fix_ssl_certificates()
    
    if success:
        logger.info("✅ SSL certificate fix completed successfully")
        logger.info("You can now run the application with:")
        logger.info("SSL_CERT_FILE=$(python -m certifi) python -m streamlit run app.py")
    else:
        logger.error("❌ SSL certificate fix failed")
        logger.info("Try running the application with SSL verification disabled")

if __name__ == "__main__":
    main()
