# Developing Your First Trading Strategy with TradeMind

## Introduction

This guide is designed for Quantitative Traders who are new to the TradeMind algorithmic trading platform. A background in quantitative finance, statistics, and Python programming is strongly recommended for leveraging the full capabilities of TradeMind. However, for this guide, a basic understanding of financial markets and common technical indicators will allow the reader to get most of the value from this guide.

This tutorial will guide you through creating, understanding, and preparing a basic trading strategy using TradeMind's Python API. We will use a simple Simple Moving Average (SMA) crossover strategy as an example, which is a common starting point for learning algorithmic trading logic.

This guide assumes you have a working TradeMind environment, including a configured Python setup where the `pyquant` library (TradeMind's Python components) is accessible, as detailed in the *TradeMind Setup Guide*.

## What You Will Learn

*   The basic structure of a TradeMind Python strategy class.
*   How to initialize strategy parameters and context.
*   How to access market data (bars) within your strategy.
*   How to implement trading logic based on technical indicators.
*   How to manage positions and execute orders.

## 1. Understanding the Core Strategy Components

TradeMind's Python strategies typically inherit from a base `Strategy` class provided by the `pyquant` library. This base class provides the framework and a `Context` object through which your strategy interacts with the trading platform (e.g., to get position information, send orders).

The two most important methods you will usually override are:

### `initialize(self) -> None`
This method is called once when your strategy is first loaded and initialized. It's where you set up parameters, subscribe to data for specific symbols, and perform any one-time setup.

### `on_bar(self, context: Context, bar_dict: dict) -> None`
This method is called for each new bar of market data that your strategy is subscribed to. This is where your primary trading logic (signal generation, order placement) will reside.
*   `context`: The `Context` object, providing access to portfolio, positions, order functions, etc.
*   `bar_dict`: A dictionary where keys are symbol strings and values are data structures (e.g., pandas DataFrames) containing the bar data (OHLCV - Open, High, Low, Close, Volume) for those symbols.

## 2. Example: Simple Moving Average (SMA) Crossover Strategy

This strategy will:

*   Calculate a short-term SMA and a long-term SMA for a given stock (e.g., AAPL).
*   Generate a buy signal when the short-term SMA crosses above the long-term SMA.
*   Generate a sell signal (or close a long position) when the short-term SMA crosses below the long-term SMA.

### Code Example

```python
# Save this as, for example, sma_strategy.py
from pyquant import Strategy, Context # OrderSide, OrderType (might be needed for specific order types)
import pandas as pd # Assuming pandas is used for DataFrames and isnan checks

class SmaStrategy(Strategy):
    def initialize(self) -> None:
        """
        Called once when the strategy is initialized.
        Set parameters and symbols here.
        """
        # Define strategy parameters
        self.parameters = {
            "symbol": "AAPL",         # The stock symbol to trade
            "fast_period": 10,        # Lookback period for the fast SMA
            "slow_period": 30,        # Lookback period for the slow SMA
            "trade_size": 100         # Number of shares to trade per signal
        }

        # Tell the context which symbols this strategy will operate on.
        # The platform will then feed bar data for these symbols to on_bar().
        self.context.symbols = [self.parameters["symbol"]]

        # You could also initialize other things here, like:
        # - Historical data needed for initial indicator calculation
        # - Logging setup specific to this strategy
        self.context.log(f"SMA Crossover Strategy for {self.parameters['symbol']} initialized.")

    def on_bar(self, context: Context, bar_dict: dict) -> None:
        """
        Called on every new bar of data for the subscribed symbols.
        Implement trading logic here.
        """
        symbol = self.parameters["symbol"]

        # Access the bar data for our target symbol.
        # We assume bar_dict[symbol] gives us a pandas DataFrame or similar
        # with a 'close' column.
        bars = bar_dict.get(symbol)
        if bars is None or 'close' not in bars or bars.empty:
            # self.context.log(f"No data or no 'close' column for {symbol}", level="WARNING")
            return

        # Ensure we have enough data to calculate SMAs
        if len(bars['close']) < self.parameters["slow_period"]:
            return

        try:
            fast_ma_series = bars['close'].rolling(window=self.parameters["fast_period"]).mean()
            slow_ma_series = bars['close'].rolling(window=self.parameters["slow_period"]).mean()
        except Exception as e:
            # self.context.log(f"Error calculating MAs for {symbol}: {e}", level="ERROR")
            return

        # Ensure we have MA values to work with (at least two for crossover detection)
        if len(fast_ma_series) < 2 or len(slow_ma_series) < 2 or \
           pd.isna(fast_ma_series.iloc[-1]) or pd.isna(fast_ma_series.iloc[-2]) or \
           pd.isna(slow_ma_series.iloc[-1]) or pd.isna(slow_ma_series.iloc[-2]):
            return

        fast_ma_prev = fast_ma_series.iloc[-2]
        fast_ma_curr = fast_ma_series.iloc[-1]
        slow_ma_prev = slow_ma_series.iloc[-2]
        slow_ma_curr = slow_ma_series.iloc[-1]

        position = context.get_position(symbol)
        current_quantity = position.quantity if position else 0

        # --- Trading Logic ---
        # Buy Signal: Fast MA crossed ABOVE Slow MA in the last period
        if fast_ma_prev <= slow_ma_prev and fast_ma_curr > slow_ma_curr:
            if current_quantity <= 0: # Not already long, or flat/short
                self.context.log(f"{bars.index[-1]}: BUY signal for {symbol}. Fast MA: {fast_ma_curr:.2f}, Slow MA: {slow_ma_curr:.2f}")
                context.buy(symbol, self.parameters["trade_size"])

        # Sell Signal (to close long): Fast MA crossed BELOW Slow MA
        elif fast_ma_prev >= slow_ma_prev and fast_ma_curr < slow_ma_curr:
            if current_quantity > 0: # Currently long
                self.context.log(f"{bars.index[-1]}: SELL signal for {symbol}. Fast MA: {fast_ma_curr:.2f}, Slow MA: {slow_ma_curr:.2f}")
                context.sell(symbol, self.parameters["trade_size"])
```

### Explanation of the Code

*   **`from pyquant import Strategy, Context`**: Imports the necessary base classes from TradeMind's library. You might need to import `OrderSide`, `OrderType` if you want to place orders other than default market orders. `import pandas as pd` is added as it's typically used for DataFrame operations like `pd.isna`.
*   **`class SmaStrategy(Strategy):`**: Defines our strategy, inheriting from `Strategy`.
*   **`initialize(self)`**:
    *   `self.parameters`: A dictionary to store configurable parameters for the strategy. This is good practice as it allows easy tuning later (e.g., during backtesting optimization).
    *   `self.context.symbols = [...]`: Tells the TradeMind platform which symbol(s) this strategy instance cares about. The platform will then ensure that the `on_bar` method receives data for these symbols.
    *   `self.context.log(...)`: An example of logging a message when the strategy initializes.
*   **`on_bar(self, context: Context, bar_dict)`**:
    *   `symbol = self.parameters["symbol"]`: Retrieves the target symbol.
    *   `bars = bar_dict.get(symbol)`: Accesses the market data for the symbol. Includes checks if `bars` is None, `close` column is missing, or `bars` is empty.
    *   **Data Check**: `if len(bars['close']) < self.parameters["slow_period"]`: Ensures we have enough historical bars to calculate the longest moving average.
    *   **SMA Calculation**: `fast_ma_series = bars['close'].rolling(window=...).mean()`. Includes basic error handling.
    *   **MA Data Check**: The check for `len(fast_ma_series) < 2` and `pd.isna(...)` ensures we have valid, non-NaN moving average values for both the current and previous periods to detect a crossover.
    *   `position = context.get_position(symbol)`: Queries the platform for the current position in the symbol.
    *   **Trading Logic**:
        *   The conditions `fast_ma_prev <= slow_ma_prev and fast_ma_curr > slow_ma_curr` check for the fast SMA crossing above the slow SMA.
        *   `context.buy(symbol, self.parameters["trade_size"])`: Sends a market buy order for the specified quantity. Similar logic applies to sell signals for closing long positions.

## 3. Using Your Strategy

Once you have saved this code (e.g., as `sma_strategy.py` in a directory known to TradeMind, perhaps configured in `config.yaml` under `strategy_engine.strategy_module_paths` as detailed in the *TradeMind Configuration Guide*):

*   **Configure TradeMind**: You would typically add an entry for this strategy in your `config.yaml` file under the `strategies` section:

    ```yaml
    # In your config.yaml
    strategies:
      - id: my_aapl_sma_crossover
        type: sma_strategy.SmaStrategy  # Assumes file is sma_strategy.py and class is SmaStrategy
        symbol: AAPL                    # This might be overridden by self.parameters in initialize if desired
        active: true
        parameters:                     # These can override defaults or be used if not set in initialize
          fast_period: 10
          slow_period: 30
          trade_size: 50 # Example: trading 50 shares
    ```
    Refer to the *TradeMind Configuration Guide* for more details on `config.yaml`.

*   **Run TradeMind**: When the platform runs, it should load, initialize, and start feeding data to your `SmaStrategy` instance.

## 4. Important Considerations & Next Steps

*   **Order Types**: The example uses basic market orders (`context.buy`, `context.sell`). `pyquant` supports other order types like `OrderType.LIMIT`, `OrderType.STOP`, etc., which would require specifying a price in the order call. See the *TradeMind Python API Reference* for details.
*   **Position Sizing**: The `trade_size` is fixed. More advanced strategies use dynamic position sizing based on risk, volatility, or account equity.
*   **Risk Management**: While global risk limits are set in `config.yaml`, strategies can implement their own risk checks (e.g., stop-loss orders, max drawdown per strategy).
*   **Data Handling**: Understand precisely how `bar_dict` provides data (e.g., pandas DataFrame columns, data types).
*   **Backtesting**: Use `pyquant.BacktestEngine` to backtest this strategy and evaluate its profitability.
*   **Parameter Optimization**: `pyquant.StrategyOptimizer` allows for finding optimal strategy parameters.

Consult the *TradeMind Python API Reference* for comprehensive details on all available functionalities.

## Conclusion

You've now seen the fundamental components of a Python trading strategy in TradeMind. This SMA crossover example provides a template for building more complex algorithms. The key is to understand the `initialize` and `on_bar` methods, how to use the `context` object, and how to process the `bar_dict` data.

Remember to thoroughly backtest and paper trade any strategy before deploying it with real capital.