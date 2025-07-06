#!/bin/bash
# Deploy to Render - True free tier hosting
# No credit card required

echo "🚀 Deploying to Render"
echo "======================"

# Check if git is configured
if ! git config user.name &> /dev/null; then
    echo "⚠️ Git not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Create render.yaml configuration
echo "⚙️ Creating Render configuration..."
cat > render.yaml << EOF
services:
  - type: web
    name: stockit-analyzer
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: STREAMLIT_SERVER_HEADLESS
        value: true
      - key: STREAMLIT_BROWSER_GATHER_USAGE_STATS
        value: false
EOF

# Create optimized requirements.txt for Render
echo "📦 Creating optimized requirements for Render..."
cat > requirements.txt << EOF
streamlit==1.46.1
pandas==2.0.3
yfinance==0.2.64
plotly==5.22.0
twilio==9.6.4
python-dotenv==1.1.1
requests==2.32.4
numpy==1.24.4
ta==0.13.0
schedule==1.3.0
pytz==2024.2
certifi==2024.8.30
EOF

# Create .env template for Render
echo "🔐 Creating environment template..."
cat > .env.example << EOF
# Render Environment Variables
# Set these in Render dashboard

TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
TARGET_PHONE_NUMBER=+919876543210
TARGET_WHATSAPP_NUMBER=+919876543210

# Render specific
RENDER=true
PORT=10000
EOF

# Update .gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << EOF

# Render
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF

# Optimize app.py for Render
echo "🔧 Optimizing app.py for Render..."
if [ -f "app.py" ]; then
    # Create backup
    cp app.py app.py.backup
    
    # Create Render-optimized app
    cat > app_render.py << 'EOF'
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import gc
import sys
from io import StringIO
import logging

# Render configuration
port = int(os.environ.get("PORT", 10000))

# Configure Streamlit for Render
st.set_page_config(
    page_title="🇮🇳 Stock Market Analyzer",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="auto"
)

# Environment configuration for Render
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import your modules with error handling
try:
    from stock_analyzer import StockAnalyzer
    from sms_service import SMSService
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all required files are in your repository")
    st.stop()

# Custom CSS for Render deployment
st.markdown("""
<style>
    .main > div {
        padding-top: 1.5rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: none;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .render-badge {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stock-card {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 0.8rem;
        padding: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    .recommendation-strong-buy {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.3rem 0;
        box-shadow: 0 4px 8px rgba(0, 184, 148, 0.3);
    }
    .recommendation-buy {
        background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.3rem 0;
        box-shadow: 0 4px 8px rgba(9, 132, 227, 0.3);
    }
    .sleep-warning {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()
if 'sms_service' not in st.session_state:
    st.session_state.sms_service = SMSService()
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Header with Render branding
st.title("🇮🇳 Indian Stock Market Analyzer")
st.markdown("""
<div class="metric-card">
    <h2>🚀 Hosted on Render</h2>
    <p>Free tier cloud hosting for your stock analysis</p>
    <div class="render-badge">💚 True Free Tier - No Credit Card Required</div>
</div>
""", unsafe_allow_html=True)

# Sleep warning for Render free tier
st.markdown("""
<div class="sleep-warning">
    ⏰ <strong>Render Free Tier Notice:</strong> This app may sleep after 15 minutes of inactivity and take 30-60 seconds to wake up. 
    For always-on hosting, consider upgrading to a paid plan.
</div>
""", unsafe_allow_html=True)

# Sidebar with system information
with st.sidebar:
    st.header("⚙️ System Status")
    st.markdown("---")
    
    # Render environment info
    is_render = os.environ.get("RENDER", False)
    st.info(f"🌐 Platform: {'Render' if is_render else 'Local'}")
    st.info(f"🔌 Port: {port}")
    
    # App status
    st.markdown("""
    **📊 App Status:**
    - ✅ Stock Data: yfinance
    - ✅ Charts: Plotly  
    - ✅ Alerts: Twilio
    - ✅ Analysis: Custom AI
    """)
    
    # Features list
    st.markdown("""
    **🎯 Features:**
    - 📈 Technical Analysis
    - 💼 Fundamental Analysis  
    - 🤖 Smart Recommendations
    - 📱 WhatsApp/SMS Alerts
    - 📊 TradingView Links
    - ⚡ Real-time Data
    """)
    
    # System resources (if available)
    try:
        import psutil
        memory = psutil.virtual_memory()
        st.metric("💾 Memory", f"{memory.percent:.1f}%")
        if memory.percent > 80:
            st.warning("⚠️ High memory usage")
    except ImportError:
        st.text("📊 Resource monitoring available")

# Wake-up mechanism for Render
if st.button("☕ Keep App Awake", help="Click to prevent the app from sleeping"):
    st.success("✅ App is now active! It will stay awake for a while.")
    st.balloons()

# Load stock symbols with caching optimized for Render
@st.cache_data(ttl=3600, max_entries=5)
def load_stock_symbols(file_path, max_symbols=100):
    """Load stock symbols with optimized caching for Render free tier"""
    try:
        with open(file_path, 'r') as f:
            symbols = [line.strip() for line in f if line.strip()]
        return symbols[:max_symbols]
    except FileNotFoundError:
        st.warning(f"📁 File {file_path} not found. Using fallback symbols.")
        # Fallback to popular Indian stocks
        return [
            'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
            'ITC.NS', 'LT.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS',
            'MARUTI.NS', 'KOTAKBANK.NS', 'HINDUNILVR.NS', 'NESTLEIND.NS',
            'BAJFINANCE.NS', 'WIPRO.NS', 'ULTRACEMCO.NS', 'TITAN.NS'
        ]

# Stock selection interface
st.header("📈 Stock Portfolio Selection")

# Create columns for different symbol sources
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="stock-card">
        <h4>📋 Default Portfolio</h4>
        <p>Curated list of top Indian blue-chip stocks</p>
    </div>
    """, unsafe_allow_html=True)
    
    default_symbols = load_stock_symbols('input.txt', max_symbols=25)  # Reduced for Render
    st.success(f"✅ {len(default_symbols)} stocks loaded")
    
    if default_symbols:
        st.text("Sample: " + ", ".join(default_symbols[:3]) + "...")

with col2:
    st.markdown("""
    <div class="stock-card">
        <h4>📊 Mutual Fund Holdings</h4>
        <p>Top stocks from mutual fund portfolios</p>
    </div>
    """, unsafe_allow_html=True)
    
    mf_symbols = load_stock_symbols('top-mutual-fund-stocks.txt', max_symbols=25)  # Reduced for Render
    st.success(f"✅ {len(mf_symbols)} stocks loaded")
    
    if mf_symbols:
        st.text("Sample: " + ", ".join(mf_symbols[:3]) + "...")

# Symbol source selection
st.markdown("### 🎯 Choose Your Analysis Source")
symbol_source = st.radio(
    "",
    ["📋 Default Portfolio", "📊 Mutual Fund Stocks", "✏️ Custom Input"],
    horizontal=True
)

if symbol_source == "📋 Default Portfolio":
    selected_symbols = default_symbols
    st.info(f"🎯 Ready to analyze {len(selected_symbols)} blue-chip stocks")
elif symbol_source == "📊 Mutual Fund Stocks":
    selected_symbols = mf_symbols
    st.info(f"🎯 Ready to analyze {len(selected_symbols)} mutual fund holdings")
else:
    st.markdown("### ✏️ Enter Custom Stock Symbols")
    custom_input = st.text_area(
        "Enter NSE stock symbols (one per line):",
        placeholder="RELIANCE.NS\nTCS.NS\nINFY.NS\nHDFCBANK.NS\nICICIBANK.NS",
        height=150,
        help="Enter valid NSE symbols ending with .NS"
    )
    selected_symbols = [s.strip().upper() for s in custom_input.split('\n') if s.strip()]
    
    # Limit for Render free tier
    if len(selected_symbols) > 20:
        st.warning("⚠️ Limited to 20 stocks on Render free tier for optimal performance")
        selected_symbols = selected_symbols[:20]
    
    if selected_symbols:
        st.success(f"✅ {len(selected_symbols)} custom symbols ready")

# Analysis section
st.header("🔍 Stock Analysis Engine")

if selected_symbols:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 Analysis Ready</h3>
        <p>{len(selected_symbols)} stocks selected for comprehensive analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis parameters
    col1, col2 = st.columns(2)
    
    with col1:
        batch_size = st.slider(
            "🔄 Batch Size (Render Optimized)",
            min_value=1,
            max_value=5,  # Reduced for Render free tier
            value=3,
            help="Smaller batches work better on Render free tier"
        )
    
    with col2:
        enable_cache = st.checkbox(
            "💾 Enable Caching",
            value=True,
            help="Cache results to improve performance"
        )
    
    # Analysis button
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyzing stocks on Render... Please wait..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process stocks in smaller batches for Render
            results = []
            total_symbols = len(selected_symbols)
            
            for i in range(0, total_symbols, batch_size):
                batch = selected_symbols[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_symbols + batch_size - 1) // batch_size
                
                status_text.text(f"📊 Processing batch {batch_num}/{total_batches} on Render...")
                
                # Analyze batch with error handling
                for j, symbol in enumerate(batch):
                    try:
                        status_text.text(f"📈 Analyzing {symbol}...")
                        result = st.session_state.analyzer.analyze_stock(symbol)
                        if result:
                            results.append(result)
                        
                        # Update progress
                        current_progress = (i + j + 1) / total_symbols
                        progress_bar.progress(current_progress)
                        
                    except Exception as e:
                        st.warning(f"⚠️ Error with {symbol}: {str(e)}")
                    
                    # Memory management for Render
                    gc.collect()
                
                # Short pause between batches for Render stability
                import time
                time.sleep(1)
            
            st.session_state.analysis_results = results
            status_text.text("✅ Analysis completed on Render!")
            
            if results:
                st.balloons()
                st.success(f"🎉 Successfully analyzed {len(results)} stocks on Render free tier!")
            else:
                st.error("❌ No analysis results. Please check your stock symbols.")

# Display results
if st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    # Categorize results
    categories = {
        'STRONG_BUY': [],
        'BUY': [],
        'WEAK_BUY': [],
        'HOLD': [],
        'WEAK_SELL': [],
        'SELL': [],
        'STRONG_SELL': []
    }
    
    for result in results:
        category = result.get('recommendation', 'HOLD')
        categories[category].append(result)
    
    # Results dashboard
    st.header("📊 Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 Strong Buy", len(categories['STRONG_BUY']))
    with col2:
        st.metric("🔵 Buy", len(categories['BUY']))
    with col3:
        st.metric("🟡 Hold", len(categories['HOLD']) + len(categories['WEAK_BUY']))
    with col4:
        st.metric("🔴 Sell", len(categories['SELL']) + len(categories['STRONG_SELL']) + len(categories['WEAK_SELL']))
    
    # Top recommendations
    if categories['STRONG_BUY']:
        st.subheader("🏆 Top Strong Buy Recommendations")
        
        for i, stock in enumerate(categories['STRONG_BUY'][:3], 1):  # Show top 3
            st.markdown(f"""
            <div class="recommendation-strong-buy">
                <h4>#{i} {stock['symbol']}</h4>
                <p><strong>Current:</strong> ₹{stock['current_price']:.2f} | 
                   <strong>Target:</strong> ₹{stock['target_price']:.2f} | 
                   <strong>Return:</strong> {stock['return_percentage']:.1f}%</p>
                <p><strong>Confidence:</strong> {stock['confidence']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

    # Alert system
    st.header("📱 Smart Alert System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 Send WhatsApp Alert", use_container_width=True):
            try:
                # Create summary message
                message = f"🇮🇳 Stock Analysis (Render)\n"
                message += f"━━━━━━━━━━━━━━━━━━━\n\n"
                message += f"🟢 Strong Buy: {len(categories['STRONG_BUY'])}\n"
                message += f"🔵 Buy: {len(categories['BUY'])}\n"
                message += f"🟡 Hold: {len(categories['HOLD'])}\n"
                message += f"🔴 Sell: {len(categories['SELL'])}\n\n"
                
                if categories['STRONG_BUY']:
                    message += "🏆 Top Picks:\n"
                    for stock in categories['STRONG_BUY'][:2]:
                        message += f"• {stock['symbol']}: +{stock['return_percentage']:.1f}%\n"
                
                message += f"\n🚀 Powered by Render"
                
                phone_number = os.environ.get("TARGET_WHATSAPP_NUMBER", "+919876543210")
                st.session_state.sms_service.send_whatsapp_alert(phone_number, message)
                st.success("✅ WhatsApp alert sent from Render!")
                
            except Exception as e:
                st.error(f"❌ WhatsApp error: {str(e)}")
    
    with col2:
        if st.button("📨 Send SMS Alert", use_container_width=True):
            try:
                strong_buy = len(categories['STRONG_BUY'])
                buy = len(categories['BUY'])
                message = f"📈 Stock Alert: {strong_buy} Strong Buy, {buy} Buy signals from Render analysis!"
                
                phone_number = os.environ.get("TARGET_PHONE_NUMBER", "+919876543210")
                st.session_state.sms_service.send_sms_alert(phone_number, message)
                st.success("✅ SMS sent from Render!")
                
            except Exception as e:
                st.error(f"❌ SMS error: {str(e)}")

else:
    # Welcome screen
    st.markdown("""
    <div class="metric-card">
        <h2>👋 Welcome to Stock Analysis on Render</h2>
        <p>Select your portfolio above and start your free analysis</p>
        <br>
        <h4>🎯 Features Available:</h4>
        <ul style="text-align: left; display: inline-block;">
            <li>📊 Technical analysis with key indicators</li>
            <li>💼 Fundamental analysis and ratios</li>
            <li>🤖 AI-powered buy/sell recommendations</li>
            <li>📱 WhatsApp & SMS alert integration</li>
            <li>📈 TradingView chart links</li>
            <li>⚡ Real-time NSE data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <p>🇮🇳 <strong>Indian Stock Market Analyzer</strong></p>
    <p>🚀 Hosted on Render Free Tier | 📊 Real-time Analysis | 📱 Smart Alerts</p>
    <p>⚡ Built with Python, Streamlit, yfinance & Twilio</p>
    <p>💚 True free hosting - No credit card required</p>
    <br>
    <p><small>⏰ App may sleep after 15 minutes of inactivity on free tier</small></p>
</div>
""", unsafe_allow_html=True)
EOF

    # Replace original app.py
    mv app_render.py app.py
    echo "✅ App optimized for Render free tier"
fi

# Commit changes
echo "📤 Committing changes to Git..."
git add .
git commit -m "Optimize for Render free tier deployment" || echo "Nothing to commit"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main || git push origin master

echo ""
echo "🎉 Render deployment preparation complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo "1. Go to: https://render.com"
echo "2. Sign up with your GitHub account (free)"
echo "3. Click 'New Web Service'"
echo "4. Connect your GitHub repository"
echo "5. Choose 'Web Service' type"
echo "6. Select branch: main (or master)"
echo "7. Runtime: Python 3"
echo "8. Build command: pip install -r requirements.txt"
echo "9. Start command: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0 --server.headless=true"
echo "10. Choose 'Free' plan"
echo "11. Click 'Create Web Service'"
echo ""
echo "🔐 Environment Variables to set in Render:"
echo "   TWILIO_ACCOUNT_SID=your_account_sid"
echo "   TWILIO_AUTH_TOKEN=your_auth_token"
echo "   TWILIO_PHONE_NUMBER=your_twilio_number"
echo "   TARGET_PHONE_NUMBER=+919876543210"
echo "   TARGET_WHATSAPP_NUMBER=+919876543210"
echo ""
echo "⚡ Your app will be live at: https://[your-app-name].onrender.com"
echo ""
echo "💚 Render Free Tier Benefits:"
echo "   • True free tier (no credit card required)"
echo "   • 512MB RAM, shared CPU"
echo "   • Custom domains included"
echo "   • SSL certificates automatic"
echo "   • GitHub integration"
echo ""
echo "⚠️ Free tier limitations:"
echo "   • App sleeps after 15 minutes of inactivity"
echo "   • 30-60 seconds wake-up time"
echo "   • 750 hours/month build time"
