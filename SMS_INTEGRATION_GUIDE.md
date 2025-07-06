# SMS Integration Guide

This guide explains how to set up SMS alerts for the Indian Stock Market Analyzer using Twilio's SMS service.

## Overview

The SMS integration provides:
- Automated daily stock alerts
- Manual alert triggers
- WhatsApp and SMS fallback support
- Formatted stock recommendations with links

## Prerequisites

- Twilio account (free trial available)
- Valid phone number for receiving SMS
- Python environment with required dependencies

## Step 1: Twilio Account Setup

### Create Account
1. Visit [Twilio.com](https://www.twilio.com/)
2. Sign up for a free account
3. Complete phone verification
4. Note your trial credit ($15 USD typically provided)

### Get Credentials
1. Navigate to [Twilio Console](https://console.twilio.com/)
2. From the dashboard, copy:
   - **Account SID**
   - **Auth Token**

### Get Phone Number
1. Go to **Phone Numbers** → **Manage** → **Buy a number**
2. Choose a number from your country or US
3. Ensure it has SMS capabilities
4. Purchase the number (uses trial credit)

## Step 2: Environment Configuration

Update your `.env` file with Twilio credentials:

```env
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1234567890
TWILIO_TO_NUMBER=+919876543210

# WhatsApp Configuration (optional)
USE_WHATSAPP=false
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886

# SMS Alert Configuration
SMS_ALERT_TIME=09:30
SMS_ALERT_TIMEZONE=Asia/Kolkata
```

### Configuration Details:

- **TWILIO_ACCOUNT_SID**: Your Account SID from Twilio Console
- **TWILIO_AUTH_TOKEN**: Your Auth Token from Twilio Console  
- **TWILIO_FROM_NUMBER**: The Twilio phone number you purchased
- **TWILIO_TO_NUMBER**: Your mobile number (with country code)
- **SMS_ALERT_TIME**: Time to send daily alerts (24-hour format)
- **SMS_ALERT_TIMEZONE**: Your timezone for scheduling

## Step 3: Phone Number Verification

### Trial Account Limitations
Twilio trial accounts can only send SMS to:
- Verified phone numbers
- The phone number used for account signup

### Verify Additional Numbers
1. Go to **Phone Numbers** → **Manage** → **Verified Caller IDs**
2. Click **Add a new number**
3. Enter the phone number to verify
4. Complete verification process

## Step 4: Test SMS Integration

Run the SMS test script:

```bash
python test_sms_integration.py
```

This script will:
- Verify your configuration
- Test Twilio connection
- Send a test SMS message
- Test the scheduler functionality

Expected output:
```
✅ TWILIO_ACCOUNT_SID: ********************************
✅ TWILIO_AUTH_TOKEN: ********************************
✅ TWILIO_FROM_NUMBER: +1234567890
✅ TWILIO_TO_NUMBER: +919876543210
✅ Test SMS sent successfully!
```

## Step 5: SSL Certificate Setup

Some systems may have SSL issues with Twilio API:

```bash
# Fix SSL certificates
python fix_ssl_certificates.py

# Or set environment variable
export SSL_CERT_FILE=$(python -m certifi)
```

## Step 6: Message Format

SMS alerts use this format:

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

### Message Components:
- **Emoji**: Visual indicator for recommendation type
- **Symbol**: Stock symbol without .NS suffix
- **Recommendation**: BUY/SELL recommendation
- **LTP**: Last Traded Price
- **Target**: Calculated target price
- **Potential**: Expected return percentage
- **Confidence**: Algorithm confidence level
- **Score**: Overall analysis score
- **Signal**: Knox divergence signal
- **TradingView**: Direct link to chart

## Step 7: Scheduling Configuration

### Automated Daily Alerts
The system can send daily alerts at a specified time:

```python
# In Streamlit app
sms_service.start_scheduler(analysis_callback)

# Or standalone
python run_sms_scheduler.py
```

### Manual Alerts
Send immediate alerts through:
- Streamlit interface "Send Now" button
- Direct API call: `sms_service.send_analysis_alerts(results)`

## Step 8: Cost Management

### Trial Account
- $15 USD credit typically provided
- SMS costs ~$0.0075 per message
- Approximately 2000 SMS messages available

### Monitor Usage
1. Check Twilio Console → Usage → Overview
2. Set up usage alerts
3. Monitor remaining credit

### Cost Optimization
- Limit alerts to actionable recommendations only
- Use daily scheduling instead of real-time alerts
- Consider WhatsApp for international recipients (lower cost)

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Error: [HTTP 401] 20003 — Authentication Error
```
**Solution**: 
- Verify Account SID and Auth Token
- Check for extra spaces in `.env` file
- Ensure credentials are from correct Twilio account

#### 2. Invalid Phone Number
```
Error: [HTTP 400] 21211 — Invalid 'To' Phone Number
```
**Solution**:
- Use international format: +919876543210
- Verify the number in Twilio Console (trial accounts)
- Check country code is correct

#### 3. Unverified Number (Trial)
```
Error: [HTTP 400] 21608 — The number is unverified
```
**Solution**:
- Verify the destination number in Twilio Console
- Or upgrade to paid account

#### 4. SSL Certificate Errors
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution**:
```bash
python fix_ssl_certificates.py
export SSL_CERT_FILE=$(python -m certifi)
```

#### 5. Geographic Permissions
```
Error: [HTTP 400] 21408 — Permission to send an SMS has not been enabled for the region
```
**Solution**:
- Enable geographic permissions in Twilio Console
- Go to Messaging → Settings → Geo Permissions

### Diagnostic Commands

```bash
# Debug environment variables
python debug_env.py

# Test SMS specifically  
python test_sms_integration.py

# Test SMS configuration only
python test_sms_config.py

# Fix SSL issues
python fix_ssl_certificates.py
```

### Log Analysis

Check application logs for detailed error information:
```bash
# In your application logs
2025-01-06 10:30:15 - ERROR - Failed to send SMS: [HTTP 400] 21211
```

## Advanced Features

### WhatsApp Fallback
When WhatsApp fails, the system automatically falls back to SMS:

```python
# This happens automatically
success = sms_service.send_whatsapp_message(message)
if not success:
    success = sms_service.send_sms_message(message)
```

### Custom Message Templates
Modify `format_stock_message()` in `sms_service.py` to customize message format.

### Rate Limiting
The system includes built-in rate limiting:
- 1-second delay between messages
- Batch processing for multiple alerts

### Alert Filtering
Only actionable recommendations are sent:
- STRONG_BUY, BUY, SELL, STRONG_SELL
- HOLD recommendations are filtered out

## Production Considerations

### Upgrade to Paid Account
For production use:
1. Add payment method to Twilio account
2. Remove trial restrictions
3. Enable automatic recharge
4. Set up usage alerts

### Phone Number Management
- Consider local numbers for better delivery rates
- Use short codes for high volume
- Enable delivery receipts for monitoring

### Security
- Store credentials securely
- Use environment variables
- Rotate Auth Tokens periodically
- Monitor usage for unauthorized access

### Monitoring
- Set up Twilio webhooks for delivery status
- Monitor error rates
- Track message costs
- Set up alerts for failures

## Support Resources

- [Twilio Documentation](https://www.twilio.com/docs/sms)
- [Twilio Console](https://console.twilio.com/)
- [Twilio Support](https://support.twilio.com/)
- [Twilio Status Page](https://status.twilio.com/)

For specific integration issues, use the provided diagnostic scripts and check Twilio Console logs.
