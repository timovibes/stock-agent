# Stock Tracking Agent

## Overview
The Stock Tracking Agent is a Python desktop application that allows users to monitor selected stocks in real time. It provides trading recommendations based on user-defined dollar thresholds for buying and selling, and visualizes stock price trends using interactive charts.

The system is designed to automate tracking so users do not have to constantly watch price charts.

## Features
- Add or remove stocks to track
- Set custom buy and sell dollar thresholds
- Real-time stock price updates
- Interactive price charts using Matplotlib
- Alerts when a stock crosses user-defined thresholds
- Analysis module providing “BUY”, “SELL”, or “HOLD” recommendations
- Responsive GUI built with Tkinter

## Requirements
- Python 3.7+
- Libraries:
  - `yfinance`
  - `matplotlib`
  - `pandas`
  - `tkinter` (usually included with Python)
- Internet connection to fetch stock data

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stock-tracker.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage
1. Open the app.
2. Enter a stock symbol, buy threshold, and sell threshold.
3. Click “Add Stock” to start tracking.
4. View real-time updates and interactive charts.
5. Alerts will pop up if a stock crosses the defined thresholds.

## Testing
Unit tests are included for critical functions like analyze_stock. Run them with:
```bash
python -m unittest test_stock_tracker.py
```

## License
MIT License
