import yfinance as yf
import pandas as pd
from datetime import datetime
import threading
import time

class StockTracker:
    def __init__(self):
        self.tracked_stocks = {}
        self.update_interval = 10000  # 10 seconds
    
    def add_stock(self, symbol, buy_threshold, sell_threshold):
        """Add a stock to tracking list"""
        symbol = symbol.strip().upper()
        
        if symbol in self.tracked_stocks:
            raise ValueError(f"{symbol} is already being tracked")
        
        if not self.validate_stock_symbol(symbol):
            raise ValueError(f"Invalid stock symbol: {symbol}")
        
        # Initialize stock data
        self.tracked_stocks[symbol] = {
            'buy_threshold': buy_threshold,  # Now in dollars
            'sell_threshold': sell_threshold,  # Now in dollars
            'current_price': None,
            'base_price': None,
            'history': [],
            'last_update': None
        }
        
        return symbol
    
    def validate_stock_symbol(self, symbol):
        """Check if stock symbol is valid by trying to fetch data"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info is not None and len(info) > 0
        except:
            return False
    
    def remove_stock(self, symbol):
        """Remove a stock from tracking"""
        if symbol in self.tracked_stocks:
            del self.tracked_stocks[symbol]
            return True
        return False
    
    def update_stock_data(self, symbol):
        """Fetch and update stock data"""
        try:
            stock = yf.Ticker(symbol)
            # Get data for the current day with 1-minute intervals
            hist = stock.history(period="1d", interval="1m")
            
            if hist.empty:
                return False
            
            current_price = hist['Close'].iloc[-1]
            current_time = hist.index[-1]
            
            # Initialize base price if this is the first update
            if (self.tracked_stocks[symbol]['base_price'] is None or 
                self.tracked_stocks[symbol]['last_update'] is None):
                self.tracked_stocks[symbol]['base_price'] = current_price
            
            # Store historical data
            self.tracked_stocks[symbol]['current_price'] = current_price
            self.tracked_stocks[symbol]['last_update'] = current_time
            
            # Add to history (keep limited size)
            self.tracked_stocks[symbol]['history'].append({
                'time': current_time,
                'price': current_price
            })
            
            # Keep only last 50 data points
            if len(self.tracked_stocks[symbol]['history']) > 50:
                self.tracked_stocks[symbol]['history'] = self.tracked_stocks[symbol]['history'][-50:]
            
            return True
            
        except Exception as e:
            print(f"Error updating {symbol}: {e}")
            return False
    
    def analyze_stock(self, symbol):
        """Analyze stock and return trading recommendation using dollar thresholds"""
        if symbol not in self.tracked_stocks:
            return "N/A"
        
        data = self.tracked_stocks[symbol]
        if data['current_price'] is None or data['base_price'] is None:
            return "Hold"
        
        current_price = data['current_price']
        base_price = data['base_price']
        price_change = current_price - base_price  # Dollar amount change
        
        buy_threshold = data['buy_threshold']  # Negative dollar amount (e.g., -2.50)
        sell_threshold = data['sell_threshold']  # Positive dollar amount (e.g., 5.00)
        
        if price_change <= buy_threshold:
            return "BUY"
        elif price_change >= sell_threshold:
            return "SELL"
        else:
            return "HOLD"
    
    def get_stock_data(self, symbol):
        """Get formatted stock data for display"""
        if symbol not in self.tracked_stocks:
            return None
        
        data = self.tracked_stocks[symbol]
        if data['current_price'] is not None and data['base_price'] is not None:
            current_price = data['current_price']
            base_price = data['base_price']
            change_amount = current_price - base_price  # Dollar change
            change_pct = ((current_price - base_price) / base_price) * 100  # Still useful for display
            recommendation = self.analyze_stock(symbol)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'base_price': base_price,
                'change_amount': change_amount,  # Dollar amount change
                'change_pct': change_pct,  # Percentage change (for reference)
                'recommendation': recommendation,
                'buy_threshold': data['buy_threshold'],
                'sell_threshold': data['sell_threshold'],
                'history': data['history']
            }
        
        return None
    
    def get_all_stocks_data(self):
        """Get data for all tracked stocks"""
        stocks_data = []
        for symbol in self.tracked_stocks.keys():
            stock_data = self.get_stock_data(symbol)
            if stock_data:
                stocks_data.append(stock_data)
        return stocks_data
    
    def check_for_alerts(self, symbol):
        """Check if a stock has triggered any alerts"""
        data = self.get_stock_data(symbol)
        if data and data['recommendation'] in ["BUY", "SELL"]:
            return {
                'symbol': symbol,
                'action': data['recommendation'],
                'price': data['current_price'],
                'change_amount': data['change_amount'],
                'change_pct': data['change_pct'],
                'message': f"{symbol}: {data['recommendation']} at ${data['current_price']:.2f} (Change: ${data['change_amount']:+.2f})"
            }
        return None
    
    def update_all_stocks(self, progress_callback=None):
        """Update all tracked stocks"""
        results = {}
        for i, symbol in enumerate(list(self.tracked_stocks.keys())):
            success = self.update_stock_data(symbol)
            results[symbol] = success
            
            if progress_callback:
                progress_callback(i + 1, len(self.tracked_stocks))
            
            time.sleep(0.5)  # Small delay to avoid rate limiting
        
        return results
    
    def clear_all_stocks(self):
        """Clear all tracked stocks"""
        self.tracked_stocks.clear()