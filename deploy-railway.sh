#!/bin/bash
# Deploy to Railway - Excellent free alternative
# $5 monthly credit (effectively free)

echo "🚀 Deploying to Railway"
echo "======================="

# Check if git is configured
if ! git config user.name &> /dev/null; then
    echo "⚠️ Git not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Create railway.json configuration
echo "⚙️ Creating Railway configuration..."
cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"
  }
}
EOF

# Create nixpacks.toml for better Python support
echo "🐍 Creating Nixpacks configuration..."
cat > nixpacks.toml << EOF
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0 --server.headless=true"
EOF

# Create optimized requirements.txt for Railway
echo "📦 Creating optimized requirements for Railway..."
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

# Create .env template
echo "🔐 Creating environment template..."
cat > .env.example << EOF
# Railway Environment Variables
# Set these in Railway dashboard

TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
TARGET_PHONE_NUMBER=+919876543210
TARGET_WHATSAPP_NUMBER=+919876543210

# Railway specific
RAILWAY_ENVIRONMENT=production
PORT=8080
EOF

# Update .gitignore
echo "📝 Updating .gitignore..."
cat >> .gitignore << EOF

# Railway
.railway/
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

# Optimize app.py for Railway
echo "🔧 Optimizing app.py for Railway..."
if [ -f "app.py" ]; then
    # Create backup
    cp app.py app.py.backup
    
    # Add Railway-specific configuration
    cat > app_railway.py << 'EOF'
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

# Railway configuration
port = int(os.environ.get("PORT", 8080))

# Configure Streamlit for Railway
st.set_page_config(
    page_title="🇮🇳 Indian Stock Market Analyzer",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="auto"
)

# Environment configuration
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import your modules
try:
    from stock_analyzer import StockAnalyzer
    from sms_service import SMSService
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please make sure all required files are in your repository")
    st.stop()

# Custom CSS for professional Railway deployment
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .railway-badge {
        background: linear-gradient(135deg, #0070f3 0%, #1db954 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .stock-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .recommendation-strong-buy {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
    }
    .recommendation-buy {
        background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.3rem 0;
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

# Header with Railway branding
st.title("🇮🇳 Indian Stock Market Analyzer")
st.markdown("""
<div class="metric-card">
    <h2>🚀 Powered by Railway</h2>
    <p>Professional stock analysis with real-time alerts</p>
    <div class="railway-badge">✨ High Performance Cloud Hosting</div>
</div>
""", unsafe_allow_html=True)

# Sidebar with Railway info
with st.sidebar:
    st.header("⚙️ System Info")
    st.markdown("---")
    
    # Railway environment info
    railway_env = os.environ.get("RAILWAY_ENVIRONMENT", "development")
    st.info(f"🌍 Environment: {railway_env}")
    st.info(f"🔌 Port: {port}")
    
    # App features
    st.markdown("""
    **🎯 Features:**
    - 📊 Technical Analysis
    - 💼 Fundamental Analysis  
    - 🤖 Smart Recommendations
    - 📱 WhatsApp/SMS Alerts
    - 📈 TradingView Integration
    - ⚡ Real-time Updates
    """)
    
    # System resources
    try:
        import psutil
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        st.metric("💾 Memory", f"{memory.percent:.1f}%")
        st.metric("🔥 CPU", f"{cpu_percent:.1f}%")
    except ImportError:
        st.text("📊 System monitoring available")

# Load stock symbols with caching
@st.cache_data(ttl=3600)
def load_stock_symbols(file_path, max_symbols=100):
    """Load stock symbols with aggressive caching for Railway"""
    try:
        with open(file_path, 'r') as f:
            symbols = [line.strip() for line in f if line.strip()]
        return symbols[:max_symbols]
    except FileNotFoundError:
        st.warning(f"📁 File {file_path} not found. Using default symbols.")
        return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                'ITC.NS', 'LT.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS']

# Stock selection interface
st.header("📈 Stock Portfolio Selection")

# Create two columns for symbol sources
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="stock-card">
        <h4>📋 Default Portfolio</h4>
        <p>Curated list of top Indian stocks</p>
    </div>
    """, unsafe_allow_html=True)
    
    default_symbols = load_stock_symbols('input.txt', max_symbols=50)
    st.success(f"✅ {len(default_symbols)} stocks loaded")
    
    if default_symbols:
        st.text("Preview: " + ", ".join(default_symbols[:4]) + "...")

with col2:
    st.markdown("""
    <div class="stock-card">
        <h4>📊 Mutual Fund Stocks</h4>
        <p>Top holdings from mutual funds</p>
    </div>
    """, unsafe_allow_html=True)
    
    mf_symbols = load_stock_symbols('top-mutual-fund-stocks.txt', max_symbols=50)
    st.success(f"✅ {len(mf_symbols)} stocks loaded")
    
    if mf_symbols:
        st.text("Preview: " + ", ".join(mf_symbols[:4]) + "...")

# Symbol source selection
st.markdown("### 🎯 Choose Your Analysis Source")
symbol_source = st.radio(
    "",
    ["📋 Default Portfolio", "📊 Mutual Fund Stocks", "✏️ Custom Input"],
    horizontal=True
)

if symbol_source == "📋 Default Portfolio":
    selected_symbols = default_symbols
    st.info(f"🎯 Analyzing {len(selected_symbols)} stocks from default portfolio")
elif symbol_source == "📊 Mutual Fund Stocks":
    selected_symbols = mf_symbols
    st.info(f"🎯 Analyzing {len(selected_symbols)} mutual fund stocks")
else:
    st.markdown("### ✏️ Enter Custom Stock Symbols")
    custom_input = st.text_area(
        "Enter NSE stock symbols (one per line):",
        placeholder="RELIANCE.NS\nTCS.NS\nINFY.NS\nHDFCBANK.NS",
        height=120,
        help="Enter valid NSE symbols ending with .NS"
    )
    selected_symbols = [s.strip().upper() for s in custom_input.split('\n') if s.strip()]
    if selected_symbols:
        st.success(f"✅ {len(selected_symbols)} custom symbols ready for analysis")

# Analysis section
st.header("🔍 Advanced Stock Analysis")

if selected_symbols:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 Ready for Analysis</h3>
        <p>Selected {len(selected_symbols)} stocks for comprehensive analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_type = st.selectbox(
            "📊 Analysis Type",
            ["Complete Analysis", "Technical Only", "Fundamental Only"]
        )
    
    with col2:
        batch_size = st.slider(
            "🔄 Batch Size",
            min_value=1,
            max_value=10,
            value=5,
            help="Process stocks in batches to optimize performance"
        )
    
    with col3:
        time_frame = st.selectbox(
            "📅 Time Frame",
            ["1 Month", "3 Months", "6 Months", "1 Year"]
        )
    
    # Start analysis button
    if st.button("🚀 Start Comprehensive Analysis", type="primary", use_container_width=True):
        with st.spinner("🔄 Performing advanced stock analysis..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process stocks in batches
            results = []
            total_symbols = len(selected_symbols)
            
            for i in range(0, total_symbols, batch_size):
                batch = selected_symbols[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_symbols + batch_size - 1) // batch_size
                
                status_text.text(f"📊 Processing batch {batch_num}/{total_batches}: {', '.join(batch)}")
                
                # Analyze batch
                for j, symbol in enumerate(batch):
                    try:
                        result = st.session_state.analyzer.analyze_stock(symbol)
                        if result:
                            results.append(result)
                    except Exception as e:
                        st.warning(f"⚠️ Error analyzing {symbol}: {str(e)}")
                    
                    # Update progress
                    current_progress = (i + j + 1) / total_symbols
                    progress_bar.progress(current_progress)
                
                # Memory management
                gc.collect()
            
            st.session_state.analysis_results = results
            status_text.text("✅ Analysis completed successfully!")
            
            # Success message
            st.balloons()
            st.success(f"🎉 Successfully analyzed {len(results)} out of {total_symbols} stocks!")

# Display comprehensive results
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
    
    # Results summary
    st.header("📊 Analysis Results Dashboard")
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🟢 Strong Buy",
            len(categories['STRONG_BUY']),
            help="Stocks with highest potential returns"
        )
    
    with col2:
        st.metric(
            "🔵 Buy",
            len(categories['BUY']),
            help="Good investment opportunities"
        )
    
    with col3:
        st.metric(
            "🟡 Hold",
            len(categories['HOLD']) + len(categories['WEAK_BUY']),
            help="Maintain current positions"
        )
    
    with col4:
        st.metric(
            "🔴 Sell",
            len(categories['SELL']) + len(categories['STRONG_SELL']) + len(categories['WEAK_SELL']),
            help="Consider exiting positions"
        )
    
    with col5:
        avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results) if results else 0
        st.metric(
            "🎯 Avg Confidence",
            f"{avg_confidence:.1f}%",
            help="Average confidence across all recommendations"
        )
    
    # Detailed results in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🟢 Strong Buy", "🔵 Buy", "🟡 Hold/Weak Buy", "🔴 Sell", "📋 Complete Report"
    ])
    
    with tab1:
        strong_buy_stocks = categories['STRONG_BUY']
        if strong_buy_stocks:
            st.subheader(f"🟢 {len(strong_buy_stocks)} Strong Buy Recommendations")
            
            # Sort by expected return
            strong_buy_stocks.sort(key=lambda x: x.get('return_percentage', 0), reverse=True)
            
            for i, stock in enumerate(strong_buy_stocks, 1):
                with st.expander(f"#{i} {stock['symbol']} - Expected Return: {stock['return_percentage']:.1f}%"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"₹{stock['current_price']:.2f}")
                    with col2:
                        st.metric("Target Price", f"₹{stock['target_price']:.2f}")
                    with col3:
                        st.metric("Expected Return", f"{stock['return_percentage']:.1f}%")
                    with col4:
                        st.metric("Confidence", f"{stock['confidence']:.1f}%")
                    
                    st.markdown(f"**📈 Analysis:** {stock.get('analysis', 'Strong technical and fundamental indicators suggest significant upside potential.')}")
                    
                    # TradingView link
                    tradingview_url = f"https://www.tradingview.com/chart/?symbol=NSE:{stock['symbol'].replace('.NS', '')}"
                    st.markdown(f"📊 [View on TradingView]({tradingview_url})")
        else:
            st.info("🔍 No strong buy recommendations found in current analysis.")
    
    # Smart Alerts section
    st.header("📱 Smart Alert System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="stock-card">
            <h4>📱 WhatsApp Alerts</h4>
            <p>Get instant notifications on your phone</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📱 Send WhatsApp Summary", use_container_width=True):
            try:
                # Create comprehensive summary
                message = f"🇮🇳 Stock Analysis Report\n"
                message += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                message += f"🟢 Strong Buy: {len(categories['STRONG_BUY'])}\n"
                message += f"🔵 Buy: {len(categories['BUY'])}\n"
                message += f"🟡 Hold: {len(categories['HOLD'])}\n"
                message += f"🔴 Sell: {len(categories['SELL'])}\n\n"
                
                if categories['STRONG_BUY']:
                    message += "🏆 Top Picks:\n"
                    for stock in categories['STRONG_BUY'][:3]:
                        message += f"• {stock['symbol']}: +{stock['return_percentage']:.1f}%\n"
                
                message += f"\n🎯 Avg Confidence: {avg_confidence:.1f}%"
                message += f"\n⚡ Powered by Railway"
                
                phone_number = os.environ.get("TARGET_WHATSAPP_NUMBER", "+919876543210")
                st.session_state.sms_service.send_whatsapp_alert(phone_number, message)
                st.success("✅ WhatsApp summary sent successfully!")
                
            except Exception as e:
                st.error(f"❌ WhatsApp error: {str(e)}")
    
    with col2:
        st.markdown("""
        <div class="stock-card">
            <h4>📨 SMS Alerts</h4>
            <p>Quick text message notifications</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📨 Send SMS Alert", use_container_width=True):
            try:
                # Create concise SMS
                strong_buy = len(categories['STRONG_BUY'])
                buy = len(categories['BUY'])
                message = f"📈 Stock Alert: {strong_buy} Strong Buy, {buy} Buy signals. "
                
                if categories['STRONG_BUY']:
                    top_pick = categories['STRONG_BUY'][0]
                    message += f"Top: {top_pick['symbol']} (+{top_pick['return_percentage']:.1f}%)"
                
                phone_number = os.environ.get("TARGET_PHONE_NUMBER", "+919876543210")
                st.session_state.sms_service.send_sms_alert(phone_number, message)
                st.success("✅ SMS alert sent successfully!")
                
            except Exception as e:
                st.error(f"❌ SMS error: {str(e)}")

else:
    # Welcome screen
    st.markdown("""
    <div class="metric-card">
        <h2>👋 Welcome to Advanced Stock Analysis</h2>
        <p>Select your stock portfolio above and click 'Start Analysis' to begin</p>
        <br>
        <h4>🎯 What You'll Get:</h4>
        <ul style="text-align: left; display: inline-block;">
            <li>📊 Technical analysis with 20+ indicators</li>
            <li>💼 Fundamental analysis and ratios</li>
            <li>🤖 AI-powered recommendations</li>
            <li>📱 Smart WhatsApp & SMS alerts</li>
            <li>📈 TradingView integration</li>
            <li>⚡ Real-time market data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <p>🇮🇳 <strong>Indian Stock Market Analyzer</strong></p>
    <p>🚀 Hosted on Railway | 📊 Real-time Analysis | 📱 Smart Alerts</p>
    <p>⚡ Built with Python, Streamlit, yfinance & Twilio</p>
    <p>💡 Professional stock analysis made simple</p>
</div>
""", unsafe_allow_html=True)
EOF

    # Replace original app.py
    mv app_railway.py app.py
    echo "✅ App optimized for Railway"
fi

# Commit changes
echo "📤 Committing changes to Git..."
git add .
git commit -m "Optimize for Railway deployment" || echo "Nothing to commit"

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Link or create project
echo "🔗 Linking Railway project..."
railway link || railway init

# Set environment variables
echo "⚙️ Setting environment variables..."
echo ""
echo "🔐 Please set these environment variables in Railway dashboard:"
echo "   TWILIO_ACCOUNT_SID=your_account_sid"
echo "   TWILIO_AUTH_TOKEN=your_auth_token"
echo "   TWILIO_PHONE_NUMBER=your_twilio_number"
echo "   TARGET_PHONE_NUMBER=+919876543210"
echo "   TARGET_WHATSAPP_NUMBER=+919876543210"
echo ""

read -p "Have you set the environment variables in Railway dashboard? (y/n): " env_set

if [ "$env_set" = "y" ] || [ "$env_set" = "Y" ]; then
    # Deploy to Railway
    echo "🚀 Deploying to Railway..."
    railway up
    
    echo ""
    echo "🎉 Deployment to Railway complete!"
    echo "================================="
    echo ""
    echo "✅ Your app is being deployed to Railway"
    echo "🌐 You'll receive a deployment URL shortly"
    echo "📊 Monitor deployment: railway logs"
    echo "🔧 Manage project: railway open"
    echo ""
    echo "⚡ Your stock analyzer will be live at: https://[your-app].railway.app"
    echo ""
    echo "🎯 Railway Benefits:"
    echo "   • $5 monthly credit (effectively free)"
    echo "   • Auto-scaling based on traffic"
    echo "   • Custom domains included"
    echo "   • No sleeping issues"
    echo "   • Professional hosting"
else
    echo "⚠️ Please set environment variables in Railway dashboard first:"
    echo "   1. Go to your Railway project dashboard"
    echo "   2. Go to Variables tab"
    echo "   3. Add the required environment variables"
    echo "   4. Run this script again"
fi
