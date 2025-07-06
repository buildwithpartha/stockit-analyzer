#!/usr/bin/env python3
"""
Fix WhatsApp messaging issues for sandbox environment
"""

import os
from dotenv import load_dotenv
from sms_service import SMSService

load_dotenv()

def test_whatsapp_solutions():
    """Test different WhatsApp messaging approaches"""
    
    print("🔍 Testing WhatsApp Solutions...")
    
    sms_service = SMSService()
    
    if not sms_service.client:
        print("❌ Twilio client not initialized")
        return
    
    # Test 1: Simple message
    print("\n📱 Test 1: Simple WhatsApp Message")
    result = sms_service.send_whatsapp_simple_alert("RELIANCE", "BUY", "1527.30")
    print(f"Result: {'✅ Success' if result else '❌ Failed'}")
    
    # Test 2: Very short message
    print("\n📱 Test 2: Very Short Message")
    try:
        whatsapp_to = f"whatsapp:{sms_service.to_number}"
        message_obj = sms_service.client.messages.create(
            body="Hello from StockAnalyzer",
            from_=sms_service.whatsapp_from,
            to=whatsapp_to
        )
        print(f"✅ Success: {message_obj.sid}")
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        if "63016" in str(e):
            print("💡 This is the 'outside window' error - need to use templates")
    
    # Test 3: Check if we can use Hello World template
    print("\n📱 Test 3: Hello World Template (if available)")
    try:
        whatsapp_to = f"whatsapp:{sms_service.to_number}"
        message_obj = sms_service.client.messages.create(
            content_sid="HXd5e82c8c0e8b1b0bd5a62a27c95b35ac8",  # Hello World template
            from_=sms_service.whatsapp_from,
            to=whatsapp_to
        )
        print(f"✅ Template Success: {message_obj.sid}")
    except Exception as e:
        print(f"❌ Template Failed: {str(e)}")
    
    print("\n💡 Solutions:")
    print("1. For immediate testing: Send a message TO the sandbox number first")
    print("2. For production: Apply for WhatsApp Business API approval")
    print("3. For now: We'll fall back to SMS when WhatsApp fails")

if __name__ == "__main__":
    test_whatsapp_solutions()
