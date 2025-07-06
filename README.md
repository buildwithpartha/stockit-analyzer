# Indian Stock Market Analyzer with SMS/WhatsApp Alerts

## 🎯 Project Overview

A comprehensive Indian stock market analysis tool that provides divergence-based trading signals with automated SMS/WhatsApp alerts. The system analyzes 73 pre-configured Indian stocks using technical and fundamental analysis, prioritizing **Rob Booker KnoxDiv divergence signals** for buy/sell recommendations.

## 🚀 Key Features

- **Knox Divergence Strategy**: Primary trading signal based on Rob Booker's divergence detection
- **73 Pre-configured Indian Stocks**: Ready-to-use stock list with NSE symbols
- **Real-time Analysis**: Technical and fundamental analysis with scoring system
- **SMS/WhatsApp Alerts**: Automated daily alerts with manual trigger support
- **Interactive Dashboard**: Beautiful Streamlit web interface
- **TradingView Integration**: Direct links to charts for each stock
- **Comprehensive Testing**: Full test suite for all components

## 📊 Analysis Strategy

### Primary Strategy: Knox Divergence (60% Weight)
- Uses Rob Booker's KnoxDiv indicator as the main signal
- Detects bullish/bearish divergences between price and RSI
- Configuration: Bars Back 200, RSI Period 7, Momentum Period 20

### Supporting Analysis:
- **Fundamental Analysis (30%)**: P/E, P/B, ROE, Revenue Growth, Profit Margins
- **Technical Analysis (10%)**: RSI, MACD, Bollinger Bands, Moving Averages

### Recommendation Levels:
- **STRONG_BUY**: Strong Bullish Divergence detected
- **BUY**: Bullish Divergence or Hidden Bullish Divergence
- **HOLD**: No clear divergence signal
- **SELL**: Bearish Divergence or Hidden Bearish Divergence
- **STRONG_SELL**: Strong Bearish Divergence detected

## 🛠 Technology Stack

```
Primary Libraries:
- streamlit==1.46.1 (Web UI framework)
- pandas==2.3.0 (Data manipulation)
- yfinance==0.2.64 (Stock data fetching)
- plotly==6.2.0 (Interactive charts)
- twilio==9.6.4 (SMS/WhatsApp messaging)
- python-dotenv==1.1.1 (Environment configuration)
- schedule==1.2.2 (Task scheduling)
- ta==0.11.0 (Technical indicators)
- requests==2.32.4 (HTTP requests)
- certifi==2025.6.15 (SSL certificates)

Additional Libraries:
- textblob==0.19.0 (Sentiment analysis - disabled)
- newsapi-python==0.2.7 (News API - disabled)
- matplotlib==3.10.3 (Charts)
- seaborn==0.13.2 (Statistical visualization)
- pytz==2025.2 (Timezone handling)
- beautifulsoup4==4.13.4 (Web scraping)
- numpy==2.3.1 (Numerical computations)
```

## 📁 Project Structure

```
indian-stock-analyzer/
├── app.py                      # Main Streamlit application
├── stock_analyzer.py           # Core analysis engine
├── sms_service.py             # SMS/WhatsApp messaging service
├── input.txt                  # Stock symbols list (73 stocks)
├── .env                       # Environment configuration
├── requirements.txt           # Python dependencies
├── WHATSAPP_SETUP_GUIDE.md   # WhatsApp setup instructions
├── SMS_INTEGRATION_GUIDE.md   # SMS integration guide
├── fix_ssl_certificates.py    # SSL certificate fix script
├── test_whatsapp.py           # WhatsApp testing script
├── test_sms_integration.py    # SMS testing script
├── test_sms_config.py         # SMS configuration test
├── run_sms_scheduler.py       # SMS scheduler runner
└── debug_env.py               # Environment debugging script
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd indian-stock-analyzer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the `.env` file and update with your credentials:

```env
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
TWILIO_TO_NUMBER=+919876543210

# WhatsApp Configuration
USE_WHATSAPP=true
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886

# SMS Alert Configuration
SMS_ALERT_TIME=09:30
SMS_ALERT_TIMEZONE=Asia/Kolkata
```

### 3. Fix SSL Certificates (if needed)

```bash
python fix_ssl_certificates.py
```

### 4. Test Configuration

```bash
# Test environment setup
python debug_env.py

# Test SMS configuration
python test_sms_config.py

# Test SMS integration
python test_sms_integration.py

# Test WhatsApp (if enabled)
python test_whatsapp.py
```

### 5. Run the Application

```bash
# Method 1: Direct run
streamlit run app.py

# Method 2: With SSL environment (recommended)
SSL_CERT_FILE=$(python -m certifi) streamlit run app.py
```

## 📱 SMS/WhatsApp Setup

### For SMS Alerts:
1. Create a [Twilio account](https://www.twilio.com/)
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Configure `.env` file
5. Follow the [SMS Integration Guide](SMS_INTEGRATION_GUIDE.md)

### For WhatsApp Alerts:
1. Complete SMS setup first
2. Join Twilio WhatsApp Sandbox
3. Send joining message to +1 415 523 8886
4. Follow the [WhatsApp Setup Guide](WHATSAPP_SETUP_GUIDE.md)

## 🔍 Using the Application

### Web Interface:

1. **Stock Selection**: 
   - Use default 73 Indian stocks from `input.txt`
   - Upload custom stock list
   - Enter stocks manually

2. **Knox Settings**:
   - Bars Back: 200 (default)
   - RSI Period: 7 (default)
   - Momentum Period: 20 (default)

3. **Analysis**:
   - Click "Analyze Stocks" to run analysis
   - View categorized recommendations
   - Check detailed metrics and charts

4. **Alerts**:
   - Start/Stop automated daily alerts
   - Send immediate alerts
   - Test messaging functionality

### Alert Format:

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

## 📈 Stock List (73 Stocks)

The system analyzes these pre-configured Indian stocks:

```
DOLATALGO.NS, GPIL.NS, MANINFRA.NS, NATIONALUM.NS, MARKSANS.NS,
HINDCOPPER.NS, JYOTHYLAB.NS, PANAMAPET.NS, JWL.NS, BEL.NS,
BSOFT.NS, VBL.NS, VESUVIUS.NS, TRITURBINE.NS, ELECON.NS,
CGPOWER.NS, IRCTC.NS, NIPPOBATRY.NS, KSB.NS, SPLPETRO.NS,
BLUEJET.NS, GABRIEL.NS, GANESHHOUC.NS, NATCOPHARM.NS, ZYDUSLIFE.NS,
TCI.NS, NEWGEN.NS, ACE.NS, INOXINDIA.NS, KPITTECH.NS,
DRREDDY.NS, KFINTECH.NS, TBOTEK.NS, DODLA.NS, ASTRAL.NS,
JBCHEPHARM.NS, DHANUKA.NS, APLAPOLLO.NS, GRINDWELL.NS, BLUESTARCO.NS,
GRAVITA.NS, CAPLIPOINT.NS, ICICIGI.NS, SHARDACROP.NS, POLYMED.NS,
INDIAMART.NS, LALPATHLAB.NS, GRSE.NS, TIINDIA.NS, MAZDOCK.NS,
SIEMENS.NS, CUMMINSIND.NS, ECLERX.NS, KEI.NS, INGERRAND.NS,
SCHAEFFLER.NS, PIIND.NS, CAMS.NS, SKFINDIA.NS, FINEORG.NS,
LTIM.NS, EICHERMOT.NS, ABB.NS, PERSISTENT.NS, POLYCAB.NS,
GODFRYPHLP.NS, APARINDS.NS, MCX.NS, VOLTAMP.NS, MARUTI.NS,
ZFCVINDIA.NS, FORCEMOT.NS, PAGEIND.NS
```

## 🧪 Testing Scripts

The project includes comprehensive testing:

```bash
# Environment debugging
python debug_env.py

# SMS configuration test
python test_sms_config.py

# SMS integration test
python test_sms_integration.py

# WhatsApp functionality test
python test_whatsapp.py

# SSL certificate fix
python fix_ssl_certificates.py

# Standalone SMS scheduler
python run_sms_scheduler.py
```

## 🔧 Troubleshooting

### Common Issues:

1. **SSL Certificate Errors**:
   ```bash
   python fix_ssl_certificates.py
   export SSL_CERT_FILE=$(python -m certifi)
   ```

2. **Twilio Authentication Errors**:
   - Check Account SID and Auth Token
   - Verify `.env` file format
   - Ensure no extra spaces

3. **Phone Number Issues**:
   - Use international format (+919876543210)
   - Verify numbers in Twilio Console (trial accounts)

4. **WhatsApp Setup Issues**:
   - Join sandbox correctly
   - Send exact joining message
   - Check sandbox limitations

5. **Analysis Failures**:
   - Check internet connection
   - Verify Yahoo Finance API access
   - Check stock symbol format

### Debug Commands:

```bash
# Check all configurations
python debug_env.py

# Test specific components
python test_sms_config.py
python test_sms_integration.py
python test_whatsapp.py

# Check application logs
streamlit run app.py --logger.level debug
```

## 📊 Performance Optimization

- **Batch Data Fetching**: Optimized API calls to Yahoo Finance
- **Session State Caching**: Results cached in Streamlit session
- **Background Threading**: SMS scheduler runs independently
- **SSL Optimization**: Custom HTTP client for better performance

## 🔒 Security Considerations

- Store credentials in `.env` file (not in code)
- Use environment variables for sensitive data
- SSL certificate verification for API calls
- Rate limiting for message sending

## 📚 Documentation

- [WhatsApp Setup Guide](WHATSAPP_SETUP_GUIDE.md)
- [SMS Integration Guide](SMS_INTEGRATION_GUIDE.md)
- Code documentation within each file
- Comprehensive test suite

## 🎯 Key Implementation Details

### Knox Divergence Algorithm:
1. Calculate RSI with 7-period (configurable)
2. Calculate momentum with 20-period (configurable)
3. Look back 200 bars (configurable)
4. Detect divergences between price and RSI
5. Classify as: STRONG_BULLISH, BULLISH, HIDDEN_BULLISH, NEUTRAL, HIDDEN_BEARISH, BEARISH, STRONG_BEARISH

### Message Delivery:
- WhatsApp first (if enabled)
- SMS fallback on WhatsApp failure
- 1-second delay between messages
- Only actionable recommendations sent

### Scheduling:
- Configurable daily alert time
- Timezone-aware scheduling
- Background thread execution
- Graceful error handling

## 📋 Requirements

- Python 3.13+ (tested on 3.13.5)
- Internet connection for stock data
- Twilio account for messaging
- Modern web browser for Streamlit interface

## 🚀 Running in Production

For production deployment:

1. **Use paid Twilio account** for unrestricted messaging
2. **Set up proper SSL certificates** for secure connections
3. **Configure proper logging** for monitoring
4. **Set up monitoring** for alert delivery
5. **Use environment variables** for all configurations
6. **Set up backup SMS providers** for redundancy

## 📄 License

This project is for educational purposes only. Please do your own research before making investment decisions.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📞 Support

For issues and questions:

1. Check troubleshooting guides
2. Run diagnostic scripts
3. Review Twilio Console logs
4. Check project documentation

## 🔮 Future Enhancements

- Multiple messaging providers
- Advanced technical indicators
- Portfolio tracking
- Real-time alerts
- Mobile application
- Database storage for historical analysis

---

**Disclaimer**: This tool is for educational and research purposes only. Stock market investments carry risks. Always conduct your own research and consider consulting with financial advisors before making investment decisions.
