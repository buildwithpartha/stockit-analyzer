# 📊 Indian Stock Market Analyzer - Recommendation Logic Guide

## 🎯 Overview

This analyzer uses **Rob Booker's Knox Divergence** strategy as the primary signal (60% weight), combined with fundamental analysis (30%) and technical indicators (10%) to generate stock recommendations.

## 🔑 Key Innovation: Envelope Condition

**CRITICAL RULE:** Any BUY recommendation with bullish divergence is ONLY made when:
```
Current Price ≤ Envelope SMA (200-period middle line)
```

This ensures we're buying below the long-term trend for better risk-reward ratios.

---

## 📈 Recommendation Categories

### 🚀 **STRONG BUY**
- **Conditions:**
  - Strong Bullish Divergence detected
  - Current Price ≤ Envelope SMA (mandatory)
- **Target:** +15% upside potential
- **Confidence:** 80-95%
- **Logic:** Strongest bullish signal with price below long-term moving average
- **Action:** High conviction buy with larger position size

### 📈 **BUY**
- **Conditions:**
  - (Bullish OR Hidden Bullish Divergence) + Price ≤ Envelope SMA + Overall Score ≥ 65
  - OR: Neutral divergence + Overall Score ≥ 65-74
- **Target:** +12% upside potential
- **Confidence:** 70-85%
- **Logic:** Good bullish signals with solid fundamentals/technicals
- **Action:** Standard buy recommendation

### 📊 **WEAK BUY**
- **Conditions:**
  - (Bullish OR Hidden Bullish Divergence) + Price ≤ Envelope SMA + Overall Score < 65
  - OR: Neutral divergence + Overall Score 55-64
- **Target:** +8% upside potential
- **Confidence:** 70-85%
- **Logic:** Moderate bullish signals, proceed with caution
- **Action:** Small position, monitor closely

### ⏸️ **HOLD**
- **Conditions:**
  - Bullish Divergence + Price > Envelope SMA (envelope rule violation)
  - OR: Strong Bullish Divergence + Price > Envelope SMA (downgraded from STRONG_BUY)
  - OR: Neutral divergence + Overall Score 45-54
- **Target:** Current price (no change expected)
- **Confidence:** 50-80%
- **Logic:** Mixed signals or price above key moving average
- **Action:** Maintain current position, wait for better entry

### 📉 **WEAK SELL**
- **Conditions:**
  - (Bearish OR Hidden Bearish Divergence) + Overall Score > 35
  - OR: Bullish Divergence + Price > Envelope SMA + Overall Score < 65
  - OR: Neutral divergence + Overall Score 35-44
- **Target:** -5% downside potential
- **Confidence:** 60-85%
- **Logic:** Early warning signs of weakness or envelope violation
- **Action:** Reduce position size, prepare for exit

### 🔻 **SELL**
- **Conditions:**
  - (Bearish OR Hidden Bearish Divergence) + Overall Score ≤ 35
  - OR: Neutral divergence + Overall Score 25-34
- **Target:** -12% downside potential
- **Confidence:** 70-85%
- **Logic:** Clear bearish signals with weak fundamentals
- **Action:** Exit position, avoid new entries

### 💥 **STRONG SELL**
- **Conditions:**
  - Strong Bearish Divergence (any price level)
  - OR: Neutral divergence + Overall Score < 25
- **Target:** -15% downside potential
- **Confidence:** 80-95%
- **Logic:** Strongest bearish signal, immediate exit recommended
- **Action:** Immediate exit, consider short position

---

## 🎯 Knox Divergence Types

### Bullish Patterns:
- **🚀 STRONG_BULLISH:** 
  - Price ≤ recent low × 1.02 (near recent low)
  - RSI > recent RSI low × 1.1 (RSI higher than recent low)
  - Momentum > 5% (strong positive momentum)
  - Score: 85

- **📈 BULLISH:**
  - Price ≤ recent low × 1.02 (near recent low)
  - RSI > recent RSI low × 1.1 (RSI higher than recent low)
  - Momentum ≤ 5% (moderate momentum)
  - Score: 75

- **🔍 HIDDEN_BULLISH:**
  - Price > recent low × 1.05 (price above recent low)
  - RSI < recent RSI low × 1.05 (RSI still low)
  - Score: 65

### Bearish Patterns:
- **🔻 STRONG_BEARISH:**
  - Price ≥ recent high × 0.98 (near recent high)
  - RSI < recent RSI high × 0.9 (RSI lower than recent high)
  - Momentum < -5% (strong negative momentum)
  - Score: 15

- **📉 BEARISH:**
  - Price ≥ recent high × 0.98 (near recent high)
  - RSI < recent RSI high × 0.9 (RSI lower than recent high)
  - Momentum ≥ -5% (moderate negative momentum)
  - Score: 25

- **🔍 HIDDEN_BEARISH:**
  - Price < recent high × 0.95 (price below recent high)
  - RSI > recent RSI high × 0.95 (RSI still high)
  - Score: 35

### Neutral:
- **➡️ NEUTRAL:**
  - No clear divergence pattern detected
  - Score: 50

---

## ⚖️ Scoring System

### Overall Score Calculation:
```
Overall Score = (Divergence Score × 60%) + (Fundamental Score × 30%) + (Technical Score × 10%)
```

### Divergence Score (60% weight):
- Based on Knox divergence pattern strength: 15-85
- Primary factor in recommendation decision

### Fundamental Score (30% weight):
- **Base Score:** 50
- **P/E Ratio:**
  - +10 if 5-25 (reasonable valuation)
  - -5 if <5 (too low, potential problems)
  - -10 if >40 (overvalued)
- **P/B Ratio:**
  - +10 if <3 (good value)
  - -10 if >5 (expensive)
- **ROE (Return on Equity):**
  - +15 if >15% (excellent)
  - +10 if 10-15% (good)
  - -15 if negative (poor management)
- **Profit Margin:**
  - +10 if >10% (healthy margins)
  - -10 if negative (losses)
- **Revenue Growth:**
  - +10 if >15% (strong growth)
  - -10 if negative (declining business)

### Technical Score (10% weight):
- **Base Score:** 50
- **RSI (14-period):**
  - +15 if <30 (oversold, potential buy)
  - +10 if 30-70 (normal range)
  - -15 if >70 (overbought, potential sell)
- **MACD:**
  - +10 if MACD > Signal (bullish)
  - -10 if MACD < Signal (bearish)
- **Moving Averages:**
  - +10 if Price > SMA50 (uptrend)
  - -10 if Price < SMA50 (downtrend)
- **Volume Trend:**
  - +5 if volume increasing (>1.2x average)
  - -5 if volume decreasing (<0.8x average)

---

## 🛡️ Envelope Condition Details

### What is the Envelope?
- **Length:** 200-period Simple Moving Average
- **Percentage:** 14% bands above and below
- **Components:**
  - Upper Envelope = SMA × 1.14
  - **Middle Line (SMA)** = 200-period average (our key reference)
  - Lower Envelope = SMA × 0.86

### Why This Condition?
1. **Better Entry Points:** Buying below long-term average
2. **Risk Management:** Reduces probability of buying at tops
3. **Institutional Support:** 200-period SMA is widely watched
4. **Statistical Edge:** Historical backtesting shows improved results

### Implementation:
```python
# Only allow buy recommendations if:
if divergence_signal in ['STRONG_BULLISH', 'BULLISH', 'HIDDEN_BULLISH']:
    if current_price <= envelope_sma:
        # Allow buy recommendation
    else:
        # Downgrade to HOLD or WEAK_SELL
```

---

## 📊 Sorting Features

The UI now includes sorting by:
- **Symbol:** Alphabetical order
- **Price:** Current stock price
- **Target:** Target price based on recommendation
- **Score:** Overall composite score (0-100)
- **Confidence:** Confidence level of recommendation
- **Return %:** Potential return percentage

Each category tab has independent sorting controls with "High to Low" or "Low to High" options.

---

## 🎯 Alert System Integration

### Actionable Stocks:
Only stocks with these recommendations trigger alerts:
- STRONG_BUY
- BUY  
- STRONG_SELL

### Consolidated WhatsApp Messages:
```
📈 Indian Stock Alert

🚀 STRONG BUY:
• TCS: ₹3420 → ₹3830 (+12.0%)
• RELIANCE: ₹1527 → ₹1756 (+15.0%)

📈 BUY:
• ITC: ₹413 → ₹462 (+12.0%)

🔻 STRONG SELL:
• BAJFINANCE: ₹925 → ₹786 (-15.0%)

Total: 4 actionable stocks
⚠️ Not investment advice
```

---

## ⚠️ Important Notes

1. **Not Financial Advice:** This is for educational purposes only
2. **Do Your Research:** Always verify with additional analysis
3. **Risk Management:** Use appropriate position sizing
4. **Market Conditions:** Consider overall market sentiment
5. **Envelope Rule:** The key safety filter for buy signals
6. **Backtesting:** Historical performance doesn't guarantee future results

---

## 🔧 Configuration

### Knox Settings (Adjustable):
- **Bars Back:** 200 (lookback period for divergence detection)
- **RSI Period:** 7 (Knox-specific RSI calculation)
- **Momentum Period:** 20 (momentum calculation period)
- **Envelope Length:** 200 (SMA period for envelope)
- **Envelope Percentage:** 14% (band width)

### Analysis Weights:
- **Divergence:** 60% (primary factor)
- **Fundamental:** 30% (company health)
- **Technical:** 10% (market momentum)

This comprehensive system provides a systematic approach to Indian stock analysis with built-in risk management through the envelope condition.
