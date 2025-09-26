import unittest
from stock_tracker import StockTracker

class TestStockTracker(unittest.TestCase):
    def setUp(self):
        # Initialize tracker
        self.tracker = StockTracker()
        
        # Add a stock with thresholds: buy if price drops $2, sell if rises $5
        self.symbol = "TEST"
        self.tracker.tracked_stocks[self.symbol] = {
            'buy_threshold': -2.0,
            'sell_threshold': 5.0,
            'current_price': None,
            'base_price': 100.0,  # starting price
            'history': [],
            'last_update': None
        }

    def test_buy_recommendation(self):
        self.tracker.tracked_stocks[self.symbol]['current_price'] = 97.5  # price drop $2.5
        result = self.tracker.analyze_stock(self.symbol)
        self.assertEqual(result, "BUY")

    def test_sell_recommendation(self):
        self.tracker.tracked_stocks[self.symbol]['current_price'] = 106.0  # price rise $6
        result = self.tracker.analyze_stock(self.symbol)
        self.assertEqual(result, "SELL")

    def test_hold_recommendation(self):
        self.tracker.tracked_stocks[self.symbol]['current_price'] = 101.0  # price change $1
        result = self.tracker.analyze_stock(self.symbol)
        self.assertEqual(result, "HOLD")


# run using python -m unittest test_stock_tracker.py
