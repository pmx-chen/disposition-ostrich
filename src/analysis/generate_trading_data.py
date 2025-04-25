# %%
import pandas as pd
import numpy as np
from pathlib import Path
import random
from datetime import datetime, timedelta
import os

# Define data directories using forward slashes
data_dir = {
    'stock_price_returns': 'C:/Users/pequa/Dropbox (Personal)/Research/my-project-shared/disposition-learning/src/data/Daily Stock Price Returns',
    'stock_price_returns_combined': 'C:/Users/pequa/Dropbox (Personal)/Research/my-project-shared/disposition-learning/src/data/Daily Stock Price Returns/combined_stock_data.csv'
}

def calculate_position_value(stock_code, date, stock_data, position):
    """Calculate the current value of a position"""
    current_price = stock_data[
        (stock_data['Stkcd'] == stock_code) & 
        (stock_data['Trddt'] == date)
    ]['Clsprc'].values[0]
    return position * current_price

def generate_trading_data(stock_data, num_investors=1000, trading_probability=0.1):
    """
    Generate simulated trading data at investor-stock-day level with disposition effects
    
    Parameters:
    -----------
    stock_data : DataFrame
        Original stock price data
    num_investors : int
        Number of investors to simulate
    trading_probability : float
        Base probability of trading on any given day
    """
    # Create list of unique stock codes and dates
    stock_codes = stock_data['Stkcd'].unique()
    dates = sorted(stock_data['Trddt'].unique())
    
    # Generate investor IDs
    investor_ids = [f'INV_{i:06d}' for i in range(1, num_investors + 1)]
    
    # Initialize empty list to store trading records
    trading_records = []
    
    # For each investor
    for investor_id in investor_ids:
        # Initialize portfolio for this investor
        portfolio = {}  # {stock_code: {'position': shares, 'avg_price': price}}
        
        # For each date
        for date in dates:
            # For each stock
            for stock_code in stock_codes:
                # Get current price
                current_price = stock_data[
                    (stock_data['Stkcd'] == stock_code) & 
                    (stock_data['Trddt'] == date)
                ]['Clsprc'].values
                
                if len(current_price) > 0:
                    price = current_price[0]
                    
                    # Check if investor has position in this stock
                    if stock_code in portfolio:
                        position = portfolio[stock_code]['position']
                        avg_price = portfolio[stock_code]['avg_price']
                        
                        # Calculate unrealized gain/loss
                        unrealized_pnl = (price - avg_price) * position
                        unrealized_pnl_pct = (price - avg_price) / avg_price
                        
                        # Adjust trading probability based on disposition effect
                        if unrealized_pnl > 0:  # Winning position
                            # Higher probability to sell winners
                            sell_prob = trading_probability * 2
                            buy_prob = trading_probability * 0.5
                        else:  # Losing position
                            # Lower probability to sell losers
                            sell_prob = trading_probability * 0.5
                            buy_prob = trading_probability * 2
                    else:
                        # No position, use base probabilities
                        sell_prob = 0  # Can't sell if no position
                        buy_prob = trading_probability
                    
                    # Generate trading decisions
                    if random.random() < buy_prob:
                        # Buy decision
                        buy_stock_cnt = random.randint(100, 10000)
                        buy_stock_amt = buy_stock_cnt * price
                        
                        # Update portfolio
                        if stock_code in portfolio:
                            # Update average price
                            total_shares = portfolio[stock_code]['position'] + buy_stock_cnt
                            total_cost = (portfolio[stock_code]['position'] * portfolio[stock_code]['avg_price']) + buy_stock_amt
                            portfolio[stock_code] = {
                                'position': total_shares,
                                'avg_price': total_cost / total_shares
                            }
                        else:
                            portfolio[stock_code] = {
                                'position': buy_stock_cnt,
                                'avg_price': price
                            }
                        
                        # Add buy record
                        trading_records.append({
                            'stock_code': stock_code,
                            'user_id': investor_id,
                            'p_date': date,
                            'buy_stock_cnt': buy_stock_cnt,
                            'buy_stock_amt': buy_stock_amt,
                            'sell_stock_cnt': 0,
                            'sell_stock_amt': 0
                        })
                    
                    if stock_code in portfolio and random.random() < sell_prob:
                        # Sell decision
                        position = portfolio[stock_code]['position']
                        sell_stock_cnt = random.randint(100, min(position, 10000))
                        sell_stock_amt = sell_stock_cnt * price
                        
                        # Update portfolio
                        portfolio[stock_code]['position'] -= sell_stock_cnt
                        if portfolio[stock_code]['position'] == 0:
                            del portfolio[stock_code]
                        
                        # Add sell record
                        trading_records.append({
                            'stock_code': stock_code,
                            'user_id': investor_id,
                            'p_date': date,
                            'buy_stock_cnt': 0,
                            'buy_stock_amt': 0,
                            'sell_stock_cnt': sell_stock_cnt,
                            'sell_stock_amt': sell_stock_amt
                        })
    
    # Convert to DataFrame
    trading_df = pd.DataFrame(trading_records)
    
    return trading_df

def main():
    try:
        # Read the combined stock data
        print("Reading stock price data...")
        stock_data = pd.read_csv(data_dir['stock_price_returns_combined'], header=0)
        stock_data['Trddt'] = pd.to_datetime(stock_data['Trddt'])
        
        # Generate trading data
        print("Generating trading data with disposition effects...")
        trading_data = generate_trading_data(stock_data)
        
        # Save the trading data
        output_path = Path(data_dir['stock_price_returns']).parent / 'simulated_trading_data.csv'
        trading_data.to_csv(output_path, index=False)
        
        print(f"\nGenerated {len(trading_data)} trading records")
        print(f"Data saved to: {output_path}")
        print("\nData preview:")
        print(trading_data.head())
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please make sure the file paths are correct and you have read/write permissions.")

if __name__ == '__main__':
    main()

    
# %%
