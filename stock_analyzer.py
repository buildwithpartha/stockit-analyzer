import yfinance as yf
import pandas as pd
import numpy as np
from ta import add_all_ta_features
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self):
        # Technical indicator settings
        self.envelope_length = 200
        self.envelope_percent = 14
        self.knox_bars_back = 200
        self.knox_rsi_period = 7
        self.knox_momentum_period = 20
        
        # Analysis weights
        self.divergence_weight = 0.60  # Primary strategy - Knox Divergence
        self.fundamental_weight = 0.30
        self.technical_weight = 0.10
        
    def analyze_stocks(self, symbols):
        """Main analysis method - returns list of stock analysis results"""
        results = []
        total_stocks = len(symbols)
        
        logger.info(f"Analyzing {total_stocks} stocks...")
        
        for i, symbol in enumerate(symbols):
            try:
                logger.info(f"Analyzing {symbol} ({i+1}/{total_stocks})")
                result = self.analyze_single_stock(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                continue
                
        logger.info(f"Analysis completed. {len(results)} stocks analyzed successfully.")
        return results
    
    def analyze_single_stock(self, symbol):
        """Analyze individual stock with technical and fundamental analysis"""
        try:
            # Fetch stock data with retries
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y", auto_adjust=True, prepost=True)
            
            if hist.empty or len(hist) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Ensure we have all required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in hist.columns:
                    if col == 'Volume':
                        # Create synthetic volume if missing
                        hist['Volume'] = (hist['High'] - hist['Low']) / hist['Close'] * 1000000
                        logger.warning(f"Volume data missing for {symbol}, created synthetic volume")
                    elif col == 'Open':
                        hist['Open'] = hist['Close'].shift(1).fillna(hist['Close'])
                    else:
                        logger.warning(f"Missing {col} data for {symbol}")
                        return None
            
            # Clean data - remove any rows with NaN values in critical columns
            hist = hist.dropna(subset=['Close', 'High', 'Low'])
            hist['Volume'] = hist['Volume'].fillna(1000000)  # Fill volume NaNs with default
            
            if len(hist) < 50:
                logger.warning(f"Insufficient clean data for {symbol}")
                return None
                
            # Get current price
            current_price = hist['Close'].iloc[-1]
            
            # Calculate technical indicators
            technical_data = self.calculate_technical_indicators(hist)
            
            # Detect Knox divergence (primary signal)
            divergence_signal, divergence_score = self.detect_knox_divergence(hist)
            
            # Get fundamental data
            fundamental_score, fundamental_metrics = self.get_fundamental_data(symbol, stock)
            
            # Calculate technical score
            technical_score = self.calculate_technical_score(technical_data)
            
            # Calculate final recommendation
            recommendation, overall_score, target_price, confidence = self.calculate_recommendation(
                technical_score, fundamental_score, divergence_signal, divergence_score, current_price, technical_data
            )
            
            # Generate TradingView link
            tradingview_link = f"https://www.tradingview.com/chart/?symbol=NSE%3A{symbol.replace('.NS', '')}"
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'recommendation': recommendation,
                'overall_score': overall_score,
                'target_price': target_price,
                'confidence': confidence,
                'divergence_signal': divergence_signal,
                'divergence_score': divergence_score,
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'fundamental_metrics': fundamental_metrics,
                'technical_data': technical_data,
                'tradingview_link': tradingview_link,
                'potential_return': round(((target_price - current_price) / current_price) * 100, 2) if target_price else 0
            }
            
        except Exception as e:
            logger.error(f"Error in single stock analysis for {symbol}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, data):
        """Calculate RSI, MACD, Bollinger Bands, Knox Divergence"""
        try:
            df = data.copy()
            
            # Ensure Volume column exists and has valid data
            if 'Volume' not in df.columns or df['Volume'].isna().all():
                logger.warning("Volume data missing, creating synthetic volume data")
                # Create synthetic volume based on price volatility
                df['Volume'] = (df['High'] - df['Low']) / df['Close'] * 1000000
                df['Volume'] = df['Volume'].fillna(1000000)
            
            # Fill any missing volume values
            df['Volume'] = df['Volume'].fillna(method='ffill').fillna(1000000)
            
            # Add all technical indicators with proper error handling
            try:
                df = add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
            except Exception as ta_error:
                logger.warning(f"Error with add_all_ta_features: {ta_error}. Using manual calculations.")
                # Calculate basic indicators manually if ta library fails
                df = self._calculate_manual_indicators(df)
            
            # Calculate custom indicators
            # RSI with Knox period
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.knox_rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.knox_rsi_period).mean()
            rs = gain / loss
            knox_rsi = 100 - (100 / (1 + rs))
            
            # Momentum
            momentum = df['Close'].pct_change(self.knox_momentum_period) * 100
            
            # Envelope
            sma_envelope = df['Close'].rolling(window=self.envelope_length).mean()
            upper_envelope = sma_envelope * (1 + self.envelope_percent / 100)
            lower_envelope = sma_envelope * (1 - self.envelope_percent / 100)
            
            return {
                'rsi_14': df['momentum_rsi'].iloc[-1] if 'momentum_rsi' in df.columns else 50,
                'knox_rsi': knox_rsi.iloc[-1] if not knox_rsi.empty else 50,
                'macd': df['trend_macd'].iloc[-1] if 'trend_macd' in df.columns else 0,
                'macd_signal': df['trend_macd_signal'].iloc[-1] if 'trend_macd_signal' in df.columns else 0,
                'bb_upper': df['volatility_bbh'].iloc[-1] if 'volatility_bbh' in df.columns else data['Close'].iloc[-1],
                'bb_lower': df['volatility_bbl'].iloc[-1] if 'volatility_bbl' in df.columns else data['Close'].iloc[-1],
                'sma_20': df['trend_sma_slow'].iloc[-1] if 'trend_sma_slow' in df.columns else data['Close'].iloc[-1],
                'sma_50': df['Close'].rolling(50).mean().iloc[-1],
                'momentum': momentum.iloc[-1] if not momentum.empty else 0,
                'envelope_sma': sma_envelope.iloc[-1] if not sma_envelope.empty else data['Close'].iloc[-1],
                'upper_envelope': upper_envelope.iloc[-1] if not upper_envelope.empty else data['Close'].iloc[-1],
                'lower_envelope': lower_envelope.iloc[-1] if not lower_envelope.empty else data['Close'].iloc[-1],
                'volume_trend': df['Volume'].rolling(20).mean().iloc[-1] / df['Volume'].rolling(50).mean().iloc[-1] if len(df) >= 50 else 1
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return self._get_default_technical_data(data)
    
    def detect_knox_divergence(self, data):
        """Implement Rob Booker KnoxDiv divergence detection"""
        try:
            if len(data) < self.knox_bars_back:
                return "NEUTRAL", 50
            
            # Calculate Knox RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.knox_rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.knox_rsi_period).mean()
            rs = gain / loss
            knox_rsi = 100 - (100 / (1 + rs))
            
            # Calculate momentum
            momentum = data['Close'].pct_change(self.knox_momentum_period)
            
            # Get recent data for analysis
            recent_data = data.tail(self.knox_bars_back)
            recent_rsi = knox_rsi.tail(self.knox_bars_back)
            recent_momentum = momentum.tail(self.knox_bars_back)
            
            # Find price highs and lows
            price_highs = recent_data['High'].rolling(window=10, center=True).max() == recent_data['High']
            price_lows = recent_data['Low'].rolling(window=10, center=True).min() == recent_data['Low']
            
            # Find RSI highs and lows
            rsi_highs = recent_rsi.rolling(window=10, center=True).max() == recent_rsi
            rsi_lows = recent_rsi.rolling(window=10, center=True).min() == recent_rsi
            
            # Detect divergences
            divergence_signal = "NEUTRAL"
            divergence_score = 50
            
            # Recent price and RSI values
            recent_price_high = recent_data['High'].tail(20).max()
            recent_price_low = recent_data['Low'].tail(20).min()
            recent_rsi_high = recent_rsi.tail(20).max()
            recent_rsi_low = recent_rsi.tail(20).min()
            
            current_price = recent_data['Close'].iloc[-1]
            current_rsi = recent_rsi.iloc[-1]
            current_momentum = recent_momentum.iloc[-1] if not recent_momentum.empty else 0
            
            # Bullish divergence detection
            if (current_price <= recent_price_low * 1.02 and  # Price near recent low
                current_rsi > recent_rsi_low * 1.1):  # RSI higher than recent low
                if current_momentum > 0.05:  # Strong momentum
                    divergence_signal = "STRONG_BULLISH"
                    divergence_score = 85
                else:
                    divergence_signal = "BULLISH"
                    divergence_score = 75
            
            # Bearish divergence detection
            elif (current_price >= recent_price_high * 0.98 and  # Price near recent high
                  current_rsi < recent_rsi_high * 0.9):  # RSI lower than recent high
                if current_momentum < -0.05:  # Strong negative momentum
                    divergence_signal = "STRONG_BEARISH"
                    divergence_score = 15
                else:
                    divergence_signal = "BEARISH"
                    divergence_score = 25
            
            # Hidden divergences
            elif (current_price > recent_price_low * 1.05 and  # Price above recent low
                  current_rsi < recent_rsi_low * 1.05):  # RSI still low
                divergence_signal = "HIDDEN_BULLISH"
                divergence_score = 65
            
            elif (current_price < recent_price_high * 0.95 and  # Price below recent high
                  current_rsi > recent_rsi_high * 0.95):  # RSI still high
                divergence_signal = "HIDDEN_BEARISH"
                divergence_score = 35
            
            return divergence_signal, divergence_score
            
        except Exception as e:
            logger.error(f"Error in Knox divergence detection: {str(e)}")
            return "NEUTRAL", 50
    
    def get_fundamental_data(self, symbol, stock):
        """Fetch P/E, P/B, ROE, revenue growth, profit margins"""
        try:
            info = stock.info
            
            # Extract fundamental metrics
            pe_ratio = info.get('trailingPE', None)
            pb_ratio = info.get('priceToBook', None)
            roe = info.get('returnOnEquity', None)
            profit_margin = info.get('profitMargins', None)
            revenue_growth = info.get('revenueGrowth', None)
            
            # Calculate fundamental score
            fundamental_score = 50  # Base score
            
            # P/E ratio scoring (lower is better, but not too low)
            if pe_ratio and 5 <= pe_ratio <= 25:
                fundamental_score += 10
            elif pe_ratio and pe_ratio < 5:
                fundamental_score -= 5  # Too low might indicate problems
            elif pe_ratio and pe_ratio > 40:
                fundamental_score -= 10
            
            # P/B ratio scoring (lower is generally better)
            if pb_ratio and pb_ratio < 3:
                fundamental_score += 10
            elif pb_ratio and pb_ratio > 5:
                fundamental_score -= 10
            
            # ROE scoring (higher is better)
            if roe and roe > 0.15:  # 15%+
                fundamental_score += 15
            elif roe and roe > 0.10:  # 10-15%
                fundamental_score += 10
            elif roe and roe < 0:
                fundamental_score -= 15
            
            # Profit margin scoring
            if profit_margin and profit_margin > 0.10:  # 10%+
                fundamental_score += 10
            elif profit_margin and profit_margin < 0:
                fundamental_score -= 10
            
            # Revenue growth scoring
            if revenue_growth and revenue_growth > 0.15:  # 15%+
                fundamental_score += 10
            elif revenue_growth and revenue_growth < 0:
                fundamental_score -= 10
            
            # Ensure score is within bounds
            fundamental_score = max(0, min(100, fundamental_score))
            
            return fundamental_score, {
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'roe': roe,
                'profit_margin': profit_margin,
                'revenue_growth': revenue_growth
            }
            
        except Exception as e:
            logger.error(f"Error getting fundamental data for {symbol}: {str(e)}")
            return 50, {}
    
    def calculate_technical_score(self, technical_data):
        """Calculate technical analysis score"""
        try:
            score = 50  # Base score
            
            # RSI scoring
            rsi = technical_data.get('rsi_14', 50)
            if 30 <= rsi <= 70:
                score += 10
            elif rsi < 30:
                score += 15  # Oversold - potential buy
            elif rsi > 70:
                score -= 15  # Overbought - potential sell
            
            # MACD scoring
            macd = technical_data.get('macd', 0)
            macd_signal = technical_data.get('macd_signal', 0)
            if macd > macd_signal:
                score += 10
            else:
                score -= 10
            
            # Moving average scoring
            current_price = technical_data.get('sma_20', 0)  # Using SMA_20 as proxy for current
            sma_50 = technical_data.get('sma_50', 0)
            if current_price > sma_50:
                score += 10
            else:
                score -= 10
            
            # Volume trend scoring
            volume_trend = technical_data.get('volume_trend', 1)
            if volume_trend > 1.2:
                score += 5
            elif volume_trend < 0.8:
                score -= 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {str(e)}")
            return 50
    
    def calculate_recommendation(self, technical_score, fundamental_score, divergence_signal, divergence_score, current_price, technical_data):
        """Generate final recommendation based on weighted scores"""
        try:
            # Weighted overall score calculation
            # Knox Divergence is the primary factor (60% weight)
            overall_score = (
                divergence_score * self.divergence_weight +
                fundamental_score * self.fundamental_weight +
                technical_score * self.technical_weight
            )
            
            # Get envelope SMA for price condition check
            envelope_sma = technical_data.get('envelope_sma', current_price)
            
            # Recommendation based on divergence signal first, then overall score
            if divergence_signal == "STRONG_BULLISH":
                # For strong bullish divergence, only recommend buy if price is below envelope SMA
                if current_price <= envelope_sma:
                    recommendation = "STRONG_BUY"
                    target_price = current_price * 1.15  # 15% target
                    confidence = min(95, 80 + (overall_score - 70) / 2)
                else:
                    # Price above SMA, downgrade to hold
                    recommendation = "HOLD"
                    target_price = current_price
                    confidence = min(70, 60 + (overall_score - 50) / 3)
            elif divergence_signal == "BULLISH" or divergence_signal == "HIDDEN_BULLISH":
                # For bullish divergence, only recommend buy if price is below envelope SMA
                if current_price <= envelope_sma:
                    if overall_score >= 65:
                        recommendation = "BUY"
                        target_price = current_price * 1.12
                    else:
                        recommendation = "WEAK_BUY"
                        target_price = current_price * 1.08
                    confidence = min(85, 70 + (overall_score - 60) / 2)
                else:
                    # Price above SMA, downgrade recommendation
                    if overall_score >= 65:
                        recommendation = "HOLD"
                        target_price = current_price
                    else:
                        recommendation = "WEAK_SELL"
                        target_price = current_price * 0.95
                    confidence = min(70, 60 + (overall_score - 50) / 3)
            elif divergence_signal == "STRONG_BEARISH":
                recommendation = "STRONG_SELL"
                target_price = current_price * 0.85  # 15% downside
                confidence = min(95, 80 + (30 - overall_score) / 2)
            elif divergence_signal == "BEARISH" or divergence_signal == "HIDDEN_BEARISH":
                if overall_score <= 35:
                    recommendation = "SELL"
                    target_price = current_price * 0.88
                else:
                    recommendation = "WEAK_SELL"
                    target_price = current_price * 0.95
                confidence = min(85, 70 + (40 - overall_score) / 2)
            else:  # NEUTRAL
                if overall_score >= 75:
                    recommendation = "STRONG_BUY"
                    target_price = current_price * 1.15
                elif overall_score >= 65:
                    recommendation = "BUY"
                    target_price = current_price * 1.12
                elif overall_score >= 55:
                    recommendation = "WEAK_BUY"
                    target_price = current_price * 1.08
                elif overall_score >= 45:
                    recommendation = "HOLD"
                    target_price = current_price
                elif overall_score >= 35:
                    recommendation = "WEAK_SELL"
                    target_price = current_price * 0.95
                elif overall_score >= 25:
                    recommendation = "SELL"
                    target_price = current_price * 0.88
                else:
                    recommendation = "STRONG_SELL"
                    target_price = current_price * 0.85
                
                confidence = min(80, 50 + abs(overall_score - 50) / 2)
            
            return recommendation, round(overall_score, 1), round(target_price, 2), round(confidence, 1)
            
        except Exception as e:
            logger.error(f"Error calculating recommendation: {str(e)}")
            return "HOLD", 50.0, current_price, 50.0
    
    def _get_default_technical_data(self, data):
        """Return default technical data when calculation fails"""
        current_price = data['Close'].iloc[-1]
        return {
            'rsi_14': 50,
            'knox_rsi': 50,
            'macd': 0,
            'macd_signal': 0,
            'bb_upper': current_price * 1.02,
            'bb_lower': current_price * 0.98,
            'sma_20': current_price,
            'sma_50': current_price,
            'momentum': 0,
            'envelope_sma': current_price,
            'upper_envelope': current_price * 1.14,
            'lower_envelope': current_price * 0.86,
            'volume_trend': 1
        }
    
    def _calculate_manual_indicators(self, df):
        """Calculate technical indicators manually when ta library fails"""
        try:
            # Calculate RSI manually
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['momentum_rsi'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD manually
            ema_12 = df['Close'].ewm(span=12).mean()
            ema_26 = df['Close'].ewm(span=26).mean()
            df['trend_macd'] = ema_12 - ema_26
            df['trend_macd_signal'] = df['trend_macd'].ewm(span=9).mean()
            
            # Calculate Bollinger Bands manually
            sma_20 = df['Close'].rolling(window=20).mean()
            std_20 = df['Close'].rolling(window=20).std()
            df['volatility_bbh'] = sma_20 + (std_20 * 2)
            df['volatility_bbl'] = sma_20 - (std_20 * 2)
            
            # Calculate SMA
            df['trend_sma_slow'] = df['Close'].rolling(window=20).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Error in manual indicator calculation: {str(e)}")
            return df
