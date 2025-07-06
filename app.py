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

# Streamlit Cloud configuration
st.set_page_config(
    page_title="🇮🇳 Indian Stock Market Analyzer",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="auto"
)

# Handle secrets for different environments
def get_secret(key, default=None):
    """Get secret from Streamlit Cloud or environment variables"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (for local development)
        return os.getenv(key, default)

# Configure environment
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Import your modules
try:
    from stock_analyzer import StockAnalyzer
    from sms_service import SMSService
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please make sure all required files are in your repository")
    st.stop()

# Custom CSS for professional look
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .recommendation-strong-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
    }
    .recommendation-buy {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        padding: 10px 0;
        font-size: 0.8rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()
if 'sms_service' not in st.session_state:
    # Initialize with secrets
    st.session_state.sms_service = SMSService()
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Main title with emoji
st.title("🇮🇳 Indian Stock Market Analyzer")
st.markdown("### 📊 Advanced Technical & Fundamental Analysis with Smart Alerts")

# Add a nice header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>🚀 Powered by Streamlit Cloud</h3>
        <p>Real-time Indian stock analysis with WhatsApp & SMS alerts</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("---")
    
    # Display app info
    st.info("""
    **🎯 Features:**
    - Technical Analysis
    - Fundamental Analysis  
    - Smart Recommendations
    - WhatsApp/SMS Alerts
    - TradingView Integration
    """)
    
    # Memory usage (if available)
    try:
        import psutil
        memory = psutil.virtual_memory()
        st.metric("Memory Usage", f"{memory.percent:.1f}%")
    except ImportError:
        st.text("Memory monitoring not available")

# Load stock symbols
@st.cache_data(ttl=3600)
def load_stock_symbols(file_path, max_symbols=100):
    """Load stock symbols with caching"""
    try:
        with open(file_path, 'r') as f:
            symbols = [line.strip() for line in f if line.strip()]
        return symbols[:max_symbols]
    except FileNotFoundError:
        st.warning(f"File {file_path} not found. Using default symbols.")
        return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']

# Stock selection
st.header("📈 Stock Selection")

col1, col2 = st.columns(2)

with col1:
    # Default portfolio
    default_symbols = load_stock_symbols('input.txt', max_symbols=50)
    st.info(f"📋 Default Portfolio: {len(default_symbols)} stocks")
    
    # Preview some symbols
    if default_symbols:
        st.text("Preview: " + ", ".join(default_symbols[:5]) + "...")

with col2:
    # Mutual fund stocks
    mf_symbols = load_stock_symbols('top-mutual-fund-stocks.txt', max_symbols=50)
    st.info(f"📊 Mutual Fund Stocks: {len(mf_symbols)} stocks")
    
    # Preview some symbols
    if mf_symbols:
        st.text("Preview: " + ", ".join(mf_symbols[:5]) + "...")

# Symbol source selection
symbol_source = st.radio(
    "Choose analysis source:",
    ["Default Portfolio", "Mutual Fund Stocks", "Custom Input"],
    horizontal=True
)

if symbol_source == "Default Portfolio":
    selected_symbols = default_symbols
elif symbol_source == "Mutual Fund Stocks":
    selected_symbols = mf_symbols
else:
    custom_input = st.text_area(
        "Enter stock symbols (one per line):",
        placeholder="RELIANCE.NS\nTCS.NS\nINFY.NS",
        height=100
    )
    selected_symbols = [s.strip() for s in custom_input.split('\n') if s.strip()]

# Analysis section
st.header("🔍 Stock Analysis")

if selected_symbols:
    st.success(f"✅ Ready to analyze {len(selected_symbols)} stocks")
    
    # Analysis button
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyzing stocks... This may take a few minutes"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process stocks
            results = []
            total_symbols = len(selected_symbols)
            
            for i, symbol in enumerate(selected_symbols):
                status_text.text(f"Analyzing {symbol}... ({i+1}/{total_symbols})")
                
                try:
                    # Analyze individual stock
                    result = st.session_state.analyzer.analyze_stock(symbol)
                    if result:
                        results.append(result)
                except Exception as e:
                    st.warning(f"Error analyzing {symbol}: {str(e)}")
                
                # Update progress
                progress_bar.progress((i + 1) / total_symbols)
                
                # Force garbage collection for memory management
                gc.collect()
            
            st.session_state.analysis_results = results
            status_text.text("✅ Analysis complete!")
            st.success(f"🎉 Analyzed {len(results)} stocks successfully!")

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
    
    # Display summary
    st.header("📊 Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        strong_buy_count = len(categories['STRONG_BUY'])
        st.metric("🟢 Strong Buy", strong_buy_count)
    
    with col2:
        buy_count = len(categories['BUY'])
        st.metric("🔵 Buy", buy_count)
    
    with col3:
        hold_count = len(categories['HOLD']) + len(categories['WEAK_BUY'])
        st.metric("🟡 Hold/Weak Buy", hold_count)
    
    with col4:
        sell_count = len(categories['SELL']) + len(categories['STRONG_SELL']) + len(categories['WEAK_SELL'])
        st.metric("🔴 Sell", sell_count)
    
    # Detailed results in tabs
    tabs = st.tabs(["🟢 Strong Buy", "🔵 Buy", "🟡 Hold", "🔴 Sell", "📋 All Results"])
    
    with tabs[0]:  # Strong Buy
        strong_buy_stocks = categories['STRONG_BUY']
        if strong_buy_stocks:
            for stock in strong_buy_stocks:
                with st.expander(f"🟢 {stock['symbol']} - ₹{stock['current_price']:.2f}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Target Price", f"₹{stock['target_price']:.2f}")
                    with col2:
                        st.metric("Expected Return", f"{stock['return_percentage']:.1f}%")
                    with col3:
                        st.metric("Confidence", f"{stock['confidence']:.1f}%")
                    
                    st.write(f"**Analysis:** {stock.get('analysis', 'Strong fundamentals and technical indicators')}")
        else:
            st.info("No strong buy recommendations at this time.")
    
    # Add WhatsApp/SMS alerts section
    st.header("📱 Smart Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 Send WhatsApp Alert", use_container_width=True):
            try:
                # Create summary message
                message = f"🇮🇳 Stock Analysis Summary\n\n"
                message += f"🟢 Strong Buy: {len(categories['STRONG_BUY'])}\n"
                message += f"🔵 Buy: {len(categories['BUY'])}\n"
                message += f"🟡 Hold: {len(categories['HOLD'])}\n"
                message += f"🔴 Sell: {len(categories['SELL'])}\n\n"
                
                if categories['STRONG_BUY']:
                    message += "Top Picks:\n"
                    for stock in categories['STRONG_BUY'][:3]:
                        message += f"• {stock['symbol']}: +{stock['return_percentage']:.1f}%\n"
                
                # Get phone number from secrets
                phone_number = get_secret("TARGET_WHATSAPP_NUMBER", "+919876543210")
                
                st.session_state.sms_service.send_whatsapp_alert(phone_number, message)
                st.success("✅ WhatsApp alert sent successfully!")
                
            except Exception as e:
                st.error(f"❌ Error sending WhatsApp alert: {str(e)}")
    
    with col2:
        if st.button("📨 Send SMS Alert", use_container_width=True):
            try:
                # Create concise SMS message
                strong_buy = len(categories['STRONG_BUY'])
                buy = len(categories['BUY'])
                message = f"Stock Alert: {strong_buy} Strong Buy, {buy} Buy signals detected. Check your portfolio!"
                
                # Get phone number from secrets
                phone_number = get_secret("TARGET_PHONE_NUMBER", "+919876543210")
                
                st.session_state.sms_service.send_sms_alert(phone_number, message)
                st.success("✅ SMS alert sent successfully!")
                
            except Exception as e:
                st.error(f"❌ Error sending SMS alert: {str(e)}")

else:
    st.info("👆 Select stocks and click 'Start Analysis' to begin")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <p>🇮🇳 <strong>Indian Stock Market Analyzer</strong></p>
    <p>🚀 Powered by Streamlit Community Cloud | 📊 Real-time Analysis | 📱 Smart Alerts</p>
    <p>⚡ Built with Streamlit, yfinance, and Twilio</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh option
if st.sidebar.checkbox("🔄 Auto-refresh (5 min)", help="Automatically refresh analysis every 5 minutes"):
    import time
    time.sleep(300)  # 5 minutes
    st.experimental_rerun()
