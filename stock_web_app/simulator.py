import numpy as np
import pandas as pd

def simulate_stock_price(initial_price, drift, volatility, time_period, dt=1/252):
    """
    Simulates stock prices using Geometric Brownian Motion.
    """
    daily_returns = np.exp((drift - 0.5 * volatility**2) * dt +
                           volatility * np.sqrt(dt) * np.random.normal(0, 1, time_period))

    price_list = [initial_price]
    for x in daily_returns:
        price_list.append(price_list[-1] * x)

    dates = pd.date_range(start='2020-01-01', periods=len(price_list))
    return pd.Series(price_list, index=dates)

def calculate_moving_averages(prices):
    """
    Calculates the moving averages for a given price series.
    """
    df = pd.DataFrame({'price': prices})
    df['MA7'] = df['price'].rolling(window=7).mean()
    df['MA30'] = df['price'].rolling(window=30).mean()
    df['MA180'] = df['price'].rolling(window=180).mean()
    df['MA365'] = df['price'].rolling(window=365).mean()
    return df

def generate_trading_signals(data):
    """
    Generates trading signals based on the Golden Cross strategy.
    """
    data['signal'] = 0.0
    data.loc[data.index[30:], 'signal'] = np.where(data['MA7'][30:] > data['MA30'][30:], 1.0, 0.0)
    data['positions'] = data['signal'].diff()
    return data

def backtest_strategy(data, initial_capital=100000.0):
    """
    Backtests a trading strategy.
    """
    portfolio = pd.DataFrame(index=data.index).fillna(0.0)
    portfolio['price'] = data['price']
    portfolio['positions'] = data['positions']
    portfolio['cash'] = initial_capital - (portfolio['positions'] * portfolio['price']).cumsum()
    portfolio['holdings'] = (portfolio['positions'].cumsum() * portfolio['price'])
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']

    return portfolio

def get_trade_ledger(portfolio):
    """
    Returns a list of trades.
    """
    # Filter out the initial row with NaN position
    ledger = portfolio[portfolio['positions'].notna() & (portfolio['positions'] != 0)].copy()
    ledger['action'] = np.where(ledger['positions'] > 0, 'Buy', 'Sell')
    ledger['shares'] = ledger['positions'].abs()
    ledger['date'] = ledger.index.strftime('%Y-%m-%d')

    return ledger[['date', 'action', 'shares', 'price']].to_dict('records')

def get_performance_summary(portfolio, initial_capital):
    """
    Calculates and returns the final portfolio performance.
    """
    final_value = portfolio['total'].iloc[-1]
    returns = (final_value - initial_capital) / initial_capital * 100

    return {
        "initial_capital": initial_capital,
        "final_value": final_value,
        "returns_pct": returns
    }

def run_simulation():
    """
    Runs the full simulation and returns all relevant data.
    """
    # Simulation parameters
    initial_price = 100.0
    drift = 0.05
    volatility = 0.2
    time_period = 252 * 2 # 2 years
    initial_capital = 100000.0

    # Run the simulation pipeline
    prices = simulate_stock_price(initial_price, drift, volatility, time_period)
    data = calculate_moving_averages(prices)
    signals = generate_trading_signals(data)
    portfolio = backtest_strategy(signals, initial_capital)

    # Get results
    ledger = get_trade_ledger(portfolio)
    performance = get_performance_summary(portfolio, initial_capital)

    # Prepare data for frontend (e.g., for Chart.js)
    chart_data = {
        'labels': data.index.strftime('%Y-%m-%d').tolist(),
        'prices': data['price'].tolist(),
        'ma7': data['MA7'].tolist(),
        'ma30': data['MA30'].tolist(),
    }

    return {
        'chart_data': chart_data,
        'ledger': ledger,
        'performance': performance
    }
