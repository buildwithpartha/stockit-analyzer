# WhatsApp Setup Guide

This guide will help you set up WhatsApp integration with the Indian Stock Market Analyzer using Twilio's WhatsApp API.

## Prerequisites

- A Twilio account (free trial is sufficient for testing)
- A WhatsApp account on your mobile device
- Python environment with required packages installed

## Step 1: Create Twilio Account

1. Go to [Twilio Console](https://console.twilio.com/)
2. Sign up for a free account or log in to existing account
3. Complete account verification if required

## Step 2: Get Twilio Credentials

1. In the Twilio Console, go to **Account Dashboard**
2. Copy your **Account SID** and **Auth Token**
3. Note down your **Twilio Phone Number** (if you have one)

## Step 3: Set Up WhatsApp Sandbox

Since WhatsApp Business API requires approval, we'll use Twilio's WhatsApp Sandbox for testing:

1. In Twilio Console, navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. You'll see instructions to join the sandbox
3. Send the joining message (like `join <sandbox-code>`) to **+1 415 523 8886** from your WhatsApp
4. You should receive a confirmation message

## Step 4: Configure Environment Variables

Update your `.env` file with the following variables:

```env
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=your_twilio_phone_number
TWILIO_TO_NUMBER=your_whatsapp_number_with_country_code

# WhatsApp Configuration
USE_WHATSAPP=true
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886

# SMS Alert Configuration
SMS_ALERT_TIME=23:52
SMS_ALERT_TIMEZONE=Asia/Kolkata
```

### Important Notes:

- **TWILIO_TO_NUMBER**: Use your WhatsApp number with country code (e.g., +919876543210)
- **WHATSAPP_FROM_NUMBER**: Keep as `whatsapp:+14155238886` for sandbox
- **TWILIO_FROM_NUMBER**: Your Twilio phone number (for SMS fallback)

## Step 5: Test WhatsApp Integration

Run the WhatsApp test script:

```bash
python test_whatsapp.py
```

This will:
- Verify your configuration
- Test the connection to Twilio
- Send a test WhatsApp message
- Test stock alert formatting

## Step 6: Production Setup (Optional)

For production use beyond sandbox limitations:

1. **Apply for WhatsApp Business API**:
   - Go to Twilio Console → Messaging → WhatsApp
   - Submit your business information for approval
   - This process can take several days

2. **Set up WhatsApp Business Profile**:
   - Complete business verification
   - Set up your business profile
   - Configure message templates

3. **Update Configuration**:
   - Replace sandbox number with your approved WhatsApp number
   - Update `WHATSAPP_FROM_NUMBER` in `.env`

## Troubleshooting

### Common Issues:

1. **"Failed to send WhatsApp message"**
   - Ensure you've joined the sandbox correctly
   - Check that your phone number format is correct
   - Verify Twilio credentials

2. **"SSL Certificate Error"**
   - Run `python fix_ssl_certificates.py`
   - Set SSL environment variables

3. **"WhatsApp not delivered"**
   - Check if your number is properly registered in sandbox
   - Ensure you haven't exceeded sandbox message limits
   - Try sending to a different verified number

4. **"Invalid credentials"**
   - Double-check Account SID and Auth Token
   - Ensure there are no extra spaces in `.env` file

### Testing Commands:

```bash
# Test environment configuration
python debug_env.py

# Test WhatsApp specifically
python test_whatsapp.py

# Test SMS fallback
python test_sms_integration.py
```

## Sandbox Limitations

The Twilio WhatsApp Sandbox has these limitations:

- Only verified phone numbers can receive messages
- Limited to 50 messages per day
- Messages may have sandbox watermarks
- No custom sender name

For production use, apply for full WhatsApp Business API access.

## Message Format

Stock alerts will be sent in this format:

```
🚀 RELIANCE - STRONG_BUY
LTP: ₹2456.75
Target: ₹2825.26
Potential: 15.0%
Confidence: 85.5%
Score: 78.2/100
Signal: STRONG_BULLISH
TradingView: https://www.tradingview.com/chart/?symbol=NSE%3ARELIANCE
```

## Scheduling Alerts

The system can send automated daily alerts:

1. **Set Alert Time**: Configure `SMS_ALERT_TIME` in `.env`
2. **Set Timezone**: Configure `SMS_ALERT_TIMEZONE` in `.env`
3. **Start Scheduler**: Use the Streamlit interface or run `python run_sms_scheduler.py`

## Support

If you encounter issues:

1. Check the [Twilio documentation](https://www.twilio.com/docs/whatsapp)
2. Review Twilio Console logs
3. Run diagnostic scripts provided
4. Check firewall/network restrictions

For WhatsApp Business API approval questions, contact Twilio support directly.
