from sms_service import SMSService

# Mock sample data
sample_stocks = [
    {'symbol': 'TCS.NS', 'recommendation': 'STRONG_BUY', 'current_price': 3420, 'target_price': 3830, 'potential_return': 12.0, 'overall_score': 78},
    {'symbol': 'RELIANCE.NS', 'recommendation': 'BUY', 'current_price': 1527, 'target_price': 1710, 'potential_return': 12.0, 'overall_score': 68},
    {'symbol': 'MARUTI.NS', 'recommendation': 'STRONG_SELL', 'current_price': 12646, 'target_price': 10749, 'potential_return': -15.0, 'overall_score': 25}
]

sms_service = SMSService()
message = sms_service.create_consolidated_alert(sample_stocks)
print('📄 Consolidated Message:')
print('-' * 50)
print(message)
print('-' * 50)

print('📤 Sending WhatsApp...')
result = sms_service.send_whatsapp_message(message)
print(f'✅ Result: {result}')
