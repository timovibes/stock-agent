import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading

from stock_tracker import StockTracker

class StockTrackingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Tracking Agent - Dollar Thresholds")
        self.root.geometry("1200x800")
        
        # Initialize the stock tracker
        self.tracker = StockTracker()
        
        self.setup_gui()
        self.start_periodic_updates()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Stock Input", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Stock Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.stock_entry = ttk.Entry(input_frame, width=15)
        self.stock_entry.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        
        # Updated labels and defaults for dollar thresholds
        ttk.Label(input_frame, text="Buy Threshold ($):").grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        self.buy_threshold_entry = ttk.Entry(input_frame, width=10)
        self.buy_threshold_entry.insert(0, "-2.00")  # Default: buy if price drops $2.00
        self.buy_threshold_entry.grid(row=0, column=3, padx=(5, 0))
        
        ttk.Label(input_frame, text="Sell Threshold ($):").grid(row=0, column=4, padx=(20, 0), sticky=tk.W)
        self.sell_threshold_entry = ttk.Entry(input_frame, width=10)
        self.sell_threshold_entry.insert(0, "5.00")  # Default: sell if price rises $5.00
        self.sell_threshold_entry.grid(row=0, column=5, padx=(5, 0))
        
        ttk.Button(input_frame, text="Add Stock", command=self.add_stock).grid(row=0, column=6, padx=(20, 0))
        ttk.Button(input_frame, text="Remove Selected", command=self.remove_stock).grid(row=0, column=7, padx=(10, 0))
        
        # Stock list section - updated columns for dollar amounts
        list_frame = ttk.LabelFrame(main_frame, text="Tracked Stocks", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        
        # Updated column names
        columns = ("Symbol", "Current Price", "Change $", "Change %", "Recommendation", "Buy At", "Sell At")
        self.stock_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        column_widths = {"Symbol": 80, "Current Price": 100, "Change $": 80, "Change %": 80, 
                        "Recommendation": 100, "Buy At": 80, "Sell At": 80}
        
        for col in columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=column_widths.get(col, 100))
        
        self.stock_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        # Chart section
        chart_frame = ttk.LabelFrame(main_frame, text="Price Chart - Select a stock to view", padding="10")
        chart_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind treeview selection to chart update
        self.stock_tree.bind('<<TreeviewSelect>>', self.on_stock_select)
        
        # Controls section
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(controls_frame, text="Update Now", command=self.update_all_stocks).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Add stocks to begin tracking")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def add_stock(self):
        symbol = self.stock_entry.get().strip().upper()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return
        
        # Validate symbol format (basic check)
        if len(symbol) < 1 or len(symbol) > 5:
            messagebox.showerror("Error", "Please enter a valid stock symbol (1-5 characters)")
            return
        
        try:
            buy_threshold = float(self.buy_threshold_entry.get())
            sell_threshold = float(self.sell_threshold_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric thresholds")
            return
        
        # Validate that buy threshold is negative and sell threshold is positive
        if buy_threshold >= 0:
            messagebox.showwarning("Warning", "Buy threshold should typically be negative (e.g., -2.00 for $2 drop)")
            if not messagebox.askyesno("Continue?", "Are you sure you want to use a positive buy threshold?"):
                return
        
        if sell_threshold <= 0:
            messagebox.showwarning("Warning", "Sell threshold should typically be positive (e.g., 5.00 for $5 gain)")
            if not messagebox.askyesno("Continue?", "Are you sure you want to use a negative sell threshold?"):
                return
        
        self.status_var.set(f"Adding {symbol}...")
        
        try:
            # Add stock to tracker
            self.tracker.add_stock(symbol, buy_threshold, sell_threshold)
            
            # Update the stock data
            if self.tracker.update_stock_data(symbol):
                self.status_var.set(f"Added {symbol} successfully")
                self.stock_entry.delete(0, tk.END)
                self.update_stock_list()
            else:
                self.tracker.remove_stock(symbol)
                self.status_var.set(f"Failed to add {symbol}")
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error adding stock")
    
    def remove_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a stock to remove")
            return
        
        for item in selected:
            symbol = self.stock_tree.item(item)['values'][0]
            if self.tracker.remove_stock(symbol):
                self.stock_tree.delete(item)
        
        self.update_chart()
        self.status_var.set("Stock removed successfully")
    
    def update_stock_list(self):
        # Clear current items
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Add updated data
        stocks_data = self.tracker.get_all_stocks_data()
        for stock_data in stocks_data:
            symbol = stock_data['symbol']
            current_price = stock_data['current_price']
            change_amount = stock_data['change_amount']
            change_pct = stock_data['change_pct']
            recommendation = stock_data['recommendation']
            buy_threshold = stock_data['buy_threshold']
            sell_threshold = stock_data['sell_threshold']
            
            # Check for alerts
            alert = self.tracker.check_for_alerts(symbol)
            if alert and abs(alert['change_amount']) > 3:  # Alert for moves > $3
                self.show_alert(alert)
            
            item_id = self.stock_tree.insert("", tk.END, values=(
                symbol,
                f"${current_price:.2f}",
                f"${change_amount:+.2f}",  # Dollar amount change
                f"{change_pct:+.2f}%",     # Percentage change for reference
                recommendation,
                f"${buy_threshold:.2f}",   # Dollar threshold
                f"${sell_threshold:.2f}"   # Dollar threshold
            ))
        
        self.status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    def show_alert(self, alert):
        """Show alert popup and log to console"""
        messagebox.showwarning("Trading Alert", alert['message'])
        print(f"ALERT: {alert['message']}")
    
    def on_stock_select(self, event):
        """Update chart when a stock is selected"""
        selected = self.stock_tree.selection()
        if selected:
            symbol = self.stock_tree.item(selected[0])['values'][0]
            self.update_chart(symbol)
    
    def update_chart(self, symbol=None):
        self.ax.clear()
        
        if not symbol:
            self.ax.text(0.5, 0.5, 'Select a stock to view chart', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        stock_data = self.tracker.get_stock_data(symbol)
        if not stock_data or len(stock_data['history']) <= 1:
            self.ax.text(0.5, 0.5, 'Insufficient data for chart', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return
        
        # Plot the chart
        times = [point['time'].to_pydatetime() for point in stock_data['history']]
        prices = [point['price'] for point in stock_data['history']]
        
        self.ax.plot(times, prices, label=symbol, marker='o', markersize=2, linewidth=2)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price ($)')
        self.ax.set_title(f'{symbol} Price Trend')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_all_stocks(self):
        def update_thread():
            self.status_var.set("Updating stock data...")
            
            def progress_callback(current, total):
                self.status_var.set(f"Updating... {current}/{total} stocks")
            
            # Update all stocks
            self.tracker.update_all_stocks(progress_callback)
            
            # Update GUI in main thread
            self.root.after(0, self.update_gui)
        
        if self.tracker.tracked_stocks:
            threading.Thread(target=update_thread, daemon=True).start()
        else:
            self.status_var.set("No stocks to update")
    
    def update_gui(self):
        self.update_stock_list()
        # Update chart if a stock is selected
        selected = self.stock_tree.selection()
        if selected:
            symbol = self.stock_tree.item(selected[0])['values'][0]
            self.update_chart(symbol)
    
    def start_periodic_updates(self):
        def periodic_update():
            self.update_all_stocks()
            self.root.after(self.tracker.update_interval, periodic_update)
        
        self.root.after(self.tracker.update_interval, periodic_update)
    
    def clear_all(self):
        if self.tracker.tracked_stocks and messagebox.askyesno("Confirm", "Clear all tracked stocks?"):
            self.tracker.clear_all_stocks()
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)
            self.update_chart()
            self.status_var.set("All stocks cleared")

def main():
    try:
        root = tk.Tk()
        app = StockTrackingGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()