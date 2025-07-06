import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import logging
from stock_analyzer import StockAnalyzer
from sms_service import SMSService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Indian Stock Market Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.strategy-info {
    background-color: #f0f8ff;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin-bottom: 2rem;
}

.rec-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid;
    background-color: #f8f9fa;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.rec-strong-buy {
    border-left-color: #28a745;
    background-color: #f8fff9;
}

.rec-buy {
    border-left-color: #17a2b8;
    background-color: #f0fcff;
}

.rec-hold {
    border-left-color: #ffc107;
    background-color: #fffdf0;
}

.rec-sell {
    border-left-color: #fd7e14;
    background-color: #fff8f0;
}

.rec-strong-sell {
    border-left-color: #dc3545;
    background-color: #fff5f5;
}

.metric-card {
    text-align: center;
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sms-status {
    padding: 0.5rem;
    border-radius: 0.25rem;
    font-weight: bold;
}

.sms-active {
    background-color: #d4edda;
    color: #155724;
}

.sms-inactive {
    background-color: #f8d7da;
    color: #721c24;
}
</style>
""", unsafe_allow_html=True)

def load_stock_symbols():
    """Load stock symbols from input.txt (one per line)"""
    try:
        with open('input.txt', 'r') as f:
            symbols = [line.strip() for line in f.readlines() if line.strip()]
        return symbols
    except FileNotFoundError:
        st.error("input.txt file not found. Please create it with stock symbols.")
        return []

def load_mutual_fund_stocks():
    """Load small cap mutual fund stocks from top-mutual-fund-stocks.txt"""
    try:
        with open('top-mutual-fund-stocks.txt', 'r') as f:
            symbols = [line.strip() for line in f.readlines() if line.strip()]
        return symbols
    except FileNotFoundError:
        st.error("top-mutual-fund-stocks.txt file not found.")
        return []

def create_recommendation_chart(results):
    """Create recommendation distribution chart"""
    if not results:
        return go.Figure()
    
    rec_counts = {}
    for stock in results:
        rec = stock['recommendation']
        rec_counts[rec] = rec_counts.get(rec, 0) + 1
    
    colors = {
        'STRONG_BUY': '#28a745',
        'BUY': '#17a2b8',
        'WEAK_BUY': '#6f42c1',
        'HOLD': '#ffc107',
        'WEAK_SELL': '#fd7e14',
        'SELL': '#dc3545',
        'STRONG_SELL': '#6c757d'
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(rec_counts.keys()),
            y=list(rec_counts.values()),
            marker_color=[colors.get(rec, '#6c757d') for rec in rec_counts.keys()],
            text=list(rec_counts.values()),
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Recommendation Distribution",
        xaxis_title="Recommendation",
        yaxis_title="Number of Stocks",
        height=400
    )
    
    return fig

def create_score_distribution_chart(results):
    """Create score distribution chart"""
    if not results:
        return go.Figure()
    
    scores = [stock['overall_score'] for stock in results]
    
    fig = go.Figure(data=[
        go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#1f77b4',
            opacity=0.7
        )
    ])
    
    fig.update_layout(
        title="Overall Score Distribution",
        xaxis_title="Score",
        yaxis_title="Number of Stocks",
        height=400
    )
    
    return fig

def display_stock_card(stock):
    """Display compact stock card"""
    rec_colors = {
        'STRONG_BUY': 'rec-strong-buy',
        'BUY': 'rec-buy',
        'WEAK_BUY': 'rec-buy',
        'HOLD': 'rec-hold',
        'WEAK_SELL': 'rec-sell', 
        'SELL': 'rec-sell',
        'STRONG_SELL': 'rec-strong-sell'
    }
    
    emoji_map = {
        'STRONG_BUY': '🚀',
        'BUY': '📈',
        'WEAK_BUY': '📊',
        'HOLD': '⏸️',
        'WEAK_SELL': '📉',
        'SELL': '🔻',
        'STRONG_SELL': '�'
    }
    
    card_class = rec_colors.get(stock['recommendation'], 'rec-hold')
    emoji = emoji_map.get(stock['recommendation'], '➡️')
    symbol_clean = stock['symbol'].replace('.NS', '')
    
    # Compact card with essential info
    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1])
    
    with col1:
        # Make symbol clickable TradingView link
        st.markdown(f"""
        <div style="font-weight: bold; font-size: 1.1em;">
            {emoji} <a href="{stock['tradingview_link']}" target="_blank" style="text-decoration: none; color: #1f77b4;">{symbol_clean}</a>
        </div>
        <div style="font-size: 0.9em; color: #666;">
            {stock['recommendation']}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Price", f"₹{stock['current_price']}", delta=f"{stock['potential_return']:+.1f}%")
    
    with col3:
        st.metric("Target", f"₹{stock['target_price']}")
    
    with col4:
        st.metric("Score", f"{stock['overall_score']}/100")
    
    with col5:
        st.metric("Confidence", f"{stock['confidence']:.0f}%")
        
    # Expandable details
    with st.expander(f"📊 Details - {symbol_clean}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Technical")
            if stock.get('technical_data'):
                tech = stock['technical_data']
                st.write(f"**RSI (14):** {tech.get('rsi_14', 0):.1f}")
                st.write(f"**Knox RSI:** {tech.get('knox_rsi', 0):.1f}")
                st.write(f"**MACD:** {tech.get('macd', 0):.4f}")
                st.write(f"**SMA 20:** ₹{tech.get('sma_20', 0):.1f}")
                st.write(f"**SMA 50:** ₹{tech.get('sma_50', 0):.1f}")
                st.write(f"**Momentum:** {tech.get('momentum', 0):.2f}%")
        
        with col2:
            st.subheader("🏢 Fundamental")
            if stock.get('fundamental_metrics'):
                metrics = stock['fundamental_metrics']
                if metrics.get('pe_ratio'):
                    st.write(f"**P/E Ratio:** {metrics['pe_ratio']:.2f}")
                if metrics.get('pb_ratio'):
                    st.write(f"**P/B Ratio:** {metrics['pb_ratio']:.2f}")
                if metrics.get('roe'):
                    st.write(f"**ROE:** {metrics['roe']*100:.1f}%" if metrics['roe'] else "ROE: N/A")
                if metrics.get('profit_margin'):
                    st.write(f"**Profit Margin:** {metrics['profit_margin']*100:.1f}%" if metrics['profit_margin'] else "Profit Margin: N/A")
                if metrics.get('revenue_growth'):
                    st.write(f"**Revenue Growth:** {metrics['revenue_growth']*100:.1f}%" if metrics['revenue_growth'] else "Revenue Growth: N/A")
            
            st.subheader("🎯 Signal Info")
            st.write(f"**Divergence:** {stock['divergence_signal']}")
            st.write(f"**Divergence Score:** {stock['divergence_score']:.1f}")
            st.write(f"**Technical Score:** {stock['technical_score']:.1f}")
            st.write(f"**Fundamental Score:** {stock['fundamental_score']:.1f}")
    
    st.divider()

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Indian Stock Market Analyzer</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = StockAnalyzer()
    if 'sms_service' not in st.session_state:
        st.session_state.sms_service = SMSService()
    if 'last_analysis_results' not in st.session_state:
        st.session_state.last_analysis_results = None
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Configuration")
        
        # Stock Selection
        st.subheader("Stock Selection")
        upload_file = st.file_uploader("Upload custom stock list", type=['txt'])
        
        if upload_file:
            content = str(upload_file.read(), "utf-8")
            symbols = [symbol.strip() for symbol in content.replace('\n', ',').split(',') if symbol.strip()]
        else:
            symbols = load_stock_symbols()
        
        # Manual stock entry
        manual_stocks = st.text_area(
            "Or enter stocks manually (comma-separated):",
            placeholder="RELIANCE.NS, TCS.NS, INFY.NS"
        )
        
        if manual_stocks:
            manual_symbols = [symbol.strip() for symbol in manual_stocks.split(',') if symbol.strip()]
            symbols = manual_symbols
        
        st.write(f"📊 **Default Stocks:** {len(symbols)}")
        
        # Show mutual fund stocks info
        mutual_fund_symbols = load_mutual_fund_stocks()
        st.write(f"📈 **Small Cap MF Stocks:** {len(mutual_fund_symbols)}")
        
        # Show preview of mutual fund stocks
        if mutual_fund_symbols:
            with st.expander("👀 Preview Small Cap MF Stocks"):
                preview_stocks = [s.replace('.NS', '') for s in mutual_fund_symbols[:15]]
                st.write(", ".join(preview_stocks))
                if len(mutual_fund_symbols) > 15:
                    st.write(f"... and {len(mutual_fund_symbols) - 15} more")
        
        # Technical Indicator Settings
        st.subheader("⚙️ Knox Settings")
        knox_bars_back = st.number_input("Bars Back", value=200, min_value=50, max_value=500)
        knox_rsi_period = st.number_input("RSI Period", value=7, min_value=5, max_value=21)
        knox_momentum_period = st.number_input("Momentum Period", value=20, min_value=10, max_value=50)
        
        # Update analyzer settings
        st.session_state.analyzer.knox_bars_back = knox_bars_back
        st.session_state.analyzer.knox_rsi_period = knox_rsi_period
        st.session_state.analyzer.knox_momentum_period = knox_momentum_period
        
        # SMS/WhatsApp Controls
        st.subheader("📱 SMS/WhatsApp Alerts")
        
        # Service status
        sms_status = st.session_state.sms_service.get_status()
        if sms_status['client_initialized']:
            st.markdown(
                '<div class="sms-status sms-active">✅ Service Active</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="sms-status sms-inactive">❌ Service Inactive</div>',
                unsafe_allow_html=True
            )
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔔 Start Alerts"):
                if st.session_state.last_analysis_results:
                    st.session_state.sms_service.start_scheduler(
                        lambda: st.session_state.last_analysis_results
                    )
                    st.success("Alerts started!")
                else:
                    st.warning("Run analysis first!")
        
        with col2:
            if st.button("🔕 Stop Alerts"):
                st.session_state.sms_service.stop_scheduler()
                st.success("Alerts stopped!")
        
        # Test connection
        if st.button("🧪 Test Connection"):
            success, message = st.session_state.sms_service.test_connection()
            if success:
                st.success(message)
            else:
                st.error(message)
        
        # Send immediate alert
        if st.button("📤 Send Now"):
            if st.session_state.last_analysis_results:
                st.session_state.sms_service.send_analysis_alerts(st.session_state.last_analysis_results)
                st.success("Consolidated alert sent!")
            else:
                st.warning("Run analysis first!")
        
        # Preview consolidated message
        if st.button("👁️ Preview Alert"):
            if st.session_state.last_analysis_results:
                actionable = [r for r in st.session_state.last_analysis_results 
                            if r['recommendation'] in ['STRONG_BUY', 'BUY', 'STRONG_SELL']]
                if actionable:
                    preview_msg = st.session_state.sms_service.create_consolidated_alert(actionable)
                    st.text_area("Consolidated Message Preview:", preview_msg, height=200)
                else:
                    st.info("No actionable stocks to preview")
            else:
                st.warning("Run analysis first!")
        
        # Display current settings
        st.info(f"""
        **Alert Time:** {sms_status['alert_time']}
        **Timezone:** {sms_status['timezone']}
        **SMS:** {'Enabled' if sms_status['sms_enabled'] else 'Disabled'}
        **WhatsApp:** {'Enabled' if sms_status['whatsapp_enabled'] else 'Disabled'}
        **Scheduler:** {'Running' if sms_status['scheduler_running'] else 'Stopped'}
        """)
    
    # Main content
    st.header("🔍 Stock Analysis")
    
    # Add Strategy Explanation
    with st.expander("📚 **Understanding Recommendation Categories & Knox Divergence Logic**", expanded=False):
        st.markdown("""
        ### 🎯 **Knox Divergence Strategy Overview**
        
        Our analyzer uses **Rob Booker's Knox Divergence** as the primary signal (60% weight), combined with fundamental (30%) and technical analysis (10%).
        
        **🔑 KEY RULE: Buy recommendations with bullish divergence are ONLY made when current price ≤ Envelope SMA (200-period)**
        
        ---
        
        ### 📊 **Recommendation Categories Explained**
        
        #### 🚀 **STRONG BUY** 
        - **Trigger:** Strong Bullish Divergence + Price ≤ Envelope SMA
        - **Target:** +15% upside potential
        - **Confidence:** 80-95%
        - **Logic:** Strongest bullish signal with price below long-term moving average
        
        #### 📈 **BUY**
        - **Trigger:** Bullish/Hidden Bullish Divergence + Price ≤ Envelope SMA + Overall Score ≥ 65
        - **OR:** Neutral divergence + Overall Score ≥ 65-74
        - **Target:** +12% upside potential  
        - **Confidence:** 70-85%
        - **Logic:** Good bullish signals with solid fundamentals/technicals
        
        #### 📊 **WEAK BUY**
        - **Trigger:** Bullish/Hidden Bullish Divergence + Price ≤ Envelope SMA + Overall Score < 65
        - **OR:** Neutral divergence + Overall Score 55-64
        - **Target:** +8% upside potential
        - **Confidence:** 70-85%
        - **Logic:** Moderate bullish signals, proceed with caution
        
        #### ⏸️ **HOLD**
        - **Trigger:** Bullish Divergence + Price > Envelope SMA (envelope rule violation)
        - **OR:** Neutral divergence + Overall Score 45-54
        - **Target:** Current price (no change expected)
        - **Confidence:** 50-80%
        - **Logic:** Mixed signals or price above key moving average
        
        #### 📉 **WEAK SELL**
        - **Trigger:** Bearish/Hidden Bearish Divergence + Overall Score > 35
        - **OR:** Bullish Divergence + Price > Envelope SMA + Overall Score < 65
        - **OR:** Neutral divergence + Overall Score 35-44
        - **Target:** -5% downside potential
        - **Confidence:** 60-85%
        - **Logic:** Early warning signs of weakness
        
        #### 🔻 **SELL**
        - **Trigger:** Bearish/Hidden Bearish Divergence + Overall Score ≤ 35
        - **OR:** Neutral divergence + Overall Score 25-34
        - **Target:** -12% downside potential
        - **Confidence:** 70-85%
        - **Logic:** Clear bearish signals with weak fundamentals
        
        #### 💥 **STRONG SELL**
        - **Trigger:** Strong Bearish Divergence (any price level)
        - **OR:** Neutral divergence + Overall Score < 25
        - **Target:** -15% downside potential
        - **Confidence:** 80-95%
        - **Logic:** Strongest bearish signal, immediate exit recommended
        
        ---
        
        ### 🎯 **Knox Divergence Types**
        
        - **🚀 STRONG_BULLISH:** Price near low + RSI higher + strong momentum (>5%)
        - **📈 BULLISH:** Price near low + RSI higher + moderate momentum
        - **🔍 HIDDEN_BULLISH:** Price above recent low + RSI still low (continuation signal)
        - **🔻 STRONG_BEARISH:** Price near high + RSI lower + strong negative momentum (<-5%)
        - **📉 BEARISH:** Price near high + RSI lower + moderate momentum  
        - **🔍 HIDDEN_BEARISH:** Price below recent high + RSI still high (continuation signal)
        - **➡️ NEUTRAL:** No clear divergence pattern detected
        
        ---
        
        ### ⚖️ **Scoring System**
        
        **Overall Score = (Divergence Score × 60%) + (Fundamental Score × 30%) + (Technical Score × 10%)**
        
        - **Divergence Score:** 15-85 based on Knox pattern strength
        - **Fundamental Score:** P/E, P/B, ROE, margins, growth analysis
        - **Technical Score:** RSI, MACD, moving averages, volume trends
        
        ---
        
        ### 🛡️ **Envelope Condition (Key Safety Filter)**
        
        **Critical Rule:** Any BUY recommendation with bullish divergence is only made if:
        **Current Price ≤ Envelope SMA (200-period middle line)**
        
        This ensures we're buying below the long-term trend, providing:
        - Better entry points
        - Reduced downside risk  
        - Higher probability of success
        - Alignment with institutional support levels
        """)
    
    # Analysis buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Analyze Default Stocks", type="primary"):
            if not symbols:
                st.error("Please provide stock symbols to analyze")
                return
            
            with st.spinner(f"Analyzing {len(symbols)} default stocks... This may take a few minutes."):
                progress_bar = st.progress(0)
                start_time = time.time()
                
                try:
                    results = st.session_state.analyzer.analyze_stocks(symbols)
                    st.session_state.last_analysis_results = results
                    
                    progress_bar.progress(100)
                    end_time = time.time()
                    
                    st.success(f"✅ Analysis completed in {end_time - start_time:.1f} seconds")
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    return
    
    with col2:
        if st.button("📊 Analyze Small Cap MF Stocks", type="secondary"):
            mutual_fund_symbols = load_mutual_fund_stocks()
            if not mutual_fund_symbols:
                st.error("Unable to load mutual fund stocks")
                return
            
            st.info(f"📈 Analyzing {len(mutual_fund_symbols)} small cap mutual fund stocks from top-mutual-fund-stocks.txt")
            
            with st.spinner(f"Analyzing {len(mutual_fund_symbols)} mutual fund stocks... This may take a few minutes."):
                progress_bar = st.progress(0)
                start_time = time.time()
                
                try:
                    results = st.session_state.analyzer.analyze_stocks(mutual_fund_symbols)
                    st.session_state.last_analysis_results = results
                    
                    progress_bar.progress(100)
                    end_time = time.time()
                    
                    st.success(f"✅ Mutual fund stocks analysis completed in {end_time - start_time:.1f} seconds")
                    st.info(f"📊 Analyzed stocks: {', '.join([s.replace('.NS', '') for s in mutual_fund_symbols[:10]])}{'...' if len(mutual_fund_symbols) > 10 else ''}")
                    
                except Exception as e:
                    st.error(f"Mutual fund analysis failed: {str(e)}")
                    return
    
    # Display results
    if st.session_state.last_analysis_results:
        results = st.session_state.last_analysis_results
        
        # Summary metrics
        st.header("📊 Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_stocks = len(results)
            st.metric("Total Analyzed", total_stocks)
        
        with col2:
            actionable = len([r for r in results if r['recommendation'] in ['STRONG_BUY', 'BUY', 'WEAK_BUY', 'WEAK_SELL', 'SELL', 'STRONG_SELL']])
            st.metric("Actionable", actionable)
        
        with col3:
            avg_score = sum(r['overall_score'] for r in results) / len(results) if results else 0
            st.metric("Avg Score", f"{avg_score:.1f}")
        
        with col4:
            strong_buys = len([r for r in results if r['recommendation'] == 'STRONG_BUY'])
            st.metric("Strong Buys", strong_buys)
        
        # Stock Analysis Results (Categorized)
        st.header("📈 Stock Analysis Results")
        
        # Quick reference card
        with st.expander("🔍 **Quick Reference - Recommendation Logic**", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **🟢 BUY SIGNALS:**
                - 🚀 **STRONG BUY:** Strong bullish divergence + price ≤ SMA
                - 📈 **BUY:** Bullish divergence + price ≤ SMA + score ≥ 65
                - 📊 **WEAK BUY:** Bullish divergence + price ≤ SMA + score < 65
                """)
            with col2:
                st.markdown("""
                **🔴 SELL SIGNALS:**
                - 💥 **STRONG SELL:** Strong bearish divergence (any price)
                - 🔻 **SELL:** Bearish divergence + score ≤ 35
                - 📉 **WEAK SELL:** Early warning signs or envelope violation
                """)
            
            st.info("📍 **Key Rule:** Buy recommendations only when price is below the 200-period Envelope SMA")
        
        # Create tabs for different categories
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🚀 STRONG BUY", "📈 BUY", "📊 WEAK BUY", "⏸️ HOLD", "📉 WEAK SELL", "🔻 SELL", "💥 STRONG SELL"])
        
        # Categorized recommendations
        recommendations = ['STRONG_BUY', 'BUY', 'WEAK_BUY', 'HOLD', 'WEAK_SELL', 'SELL', 'STRONG_SELL']
        tabs = [tab1, tab2, tab3, tab4, tab5, tab6, tab7]
        
        for tab, rec in zip(tabs, recommendations):
            with tab:
                stocks_in_category = [stock for stock in results if stock['recommendation'] == rec]
                
                if stocks_in_category:
                    st.write(f"**{len(stocks_in_category)} stocks** with {rec.replace('_', ' ')} recommendation")
                    
                    # Sorting controls
                    col_sort1, col_sort2 = st.columns([1, 3])
                    with col_sort1:
                        sort_by = st.selectbox(
                            "Sort by:",
                            ["Score", "Symbol", "Price", "Target", "Confidence", "Return %"],
                            key=f"sort_{rec}"
                        )
                    with col_sort2:
                        sort_order = st.radio(
                            "Order:",
                            ["High to Low", "Low to High"],
                            key=f"order_{rec}",
                            horizontal=True
                        )
                    
                    # Apply sorting
                    if sort_by == "Score":
                        stocks_in_category.sort(key=lambda x: x['overall_score'], reverse=(sort_order == "High to Low"))
                    elif sort_by == "Symbol":
                        stocks_in_category.sort(key=lambda x: x['symbol'].replace('.NS', ''), reverse=(sort_order == "High to Low"))
                    elif sort_by == "Price":
                        stocks_in_category.sort(key=lambda x: x['current_price'], reverse=(sort_order == "High to Low"))
                    elif sort_by == "Target":
                        stocks_in_category.sort(key=lambda x: x['target_price'], reverse=(sort_order == "High to Low"))
                    elif sort_by == "Confidence":
                        stocks_in_category.sort(key=lambda x: x['confidence'], reverse=(sort_order == "High to Low"))
                    elif sort_by == "Return %":
                        stocks_in_category.sort(key=lambda x: x['potential_return'], reverse=(sort_order == "High to Low"))
                    
                    # Display sortable header row with clickable columns
                    st.markdown("---")
                    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1])
                    with col1:
                        st.markdown("**🏢 Symbol**")
                    with col2:
                        st.markdown("**💰 Price**")
                    with col3:
                        st.markdown("**🎯 Target**")
                    with col4:
                        st.markdown("**📊 Score**")
                    with col5:
                        st.markdown("**🔥 Confidence**")
                    
                    st.divider()
                    
                    for stock in stocks_in_category:
                        display_stock_card(stock)
                else:
                    st.info(f"No stocks found with {rec.replace('_', ' ')} recommendation")
        
        # Charts Section (Moved to end)
        st.header("📊 Analysis Charts")
        
        col1, col2 = st.columns(2)
        with col1:
            fig1 = create_recommendation_chart(results)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_score_distribution_chart(results)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Export functionality
        st.header("📁 Export Results")
        
        # Create DataFrame for export
        export_data = []
        for stock in results:
            export_data.append({
                'Symbol': stock['symbol'],
                'Recommendation': stock['recommendation'],
                'Current Price': stock['current_price'],
                'Target Price': stock['target_price'],
                'Potential Return %': stock['potential_return'],
                'Overall Score': stock['overall_score'],
                'Confidence %': stock['confidence'],
                'Divergence Signal': stock['divergence_signal'],
                'Technical Score': stock['technical_score'],
                'Fundamental Score': stock['fundamental_score']
            })
        
        df = pd.DataFrame(export_data)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            if st.button("📊 Show Data Table"):
                st.dataframe(df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**Disclaimer:** This is for educational purposes only. Please do your own research before making investment decisions.")

if __name__ == "__main__":
    main()
