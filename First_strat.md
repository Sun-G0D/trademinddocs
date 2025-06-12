# Developing Your First Trading Strategy with TradeMind

## Introduction

This guide is designed for Quantitative Traders who are new to the TradeMind algorithmic trading platform. A background in quantitative finance, statistics, and Python programming is strongly recommended for leveraging the full capabilities of TradeMind. However, for this guide, a basic understanding of financial markets and common technical indicators will allow the reader to get most of the value from this guide.

This tutorial will guide you through creating, understanding, and preparing a basic trading strategy using TradeMind's Python API. We will use a simple Simple Moving Average (SMA) crossover strategy as an example, which is a common starting point for learning algorithmic trading logic.

This guide assumes you have a working TradeMind environment, including a configured Python setup where the `pyquant` library (TradeMind's Python components) is accessible, as detailed in the [*TradeMind Setup Guide*](Setup_guide.md).

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

You can download the complete example strategy file here:

<p><a href="./sma_strategy.py" download="sma_strategy.py">Download sma_strategy.py</a></p>

### Explanation of the Code

Let's break down the `sma_strategy.py` file snippet by snippet.

**1. Imports and Class Definition:**
```python
# Save this as, for example, sma_strategy.py
from pyquant import Strategy, Context # OrderSide, OrderType (might be needed for specific order types)
import pandas as pd # Assuming pandas is used for DataFrames and isnan checks

class SmaStrategy(Strategy):
    # ... strategy methods will follow
```
*   **`from pyquant import Strategy, Context`**: This line imports the fundamental `Strategy` class that all TradeMind strategies must inherit from, and the `Context` object, which provides the strategy with access to platform functionalities and information. Other objects like `OrderSide` and `OrderType` might be imported if you plan to use specific order types beyond simple market orders.
*   **`import pandas as pd`**: Pandas is a widely used library in Python for data analysis. Here, it's anticipated to be used for handling bar data (which is often in a Pandas DataFrame format) and for operations like checking for `NaN` (Not a Number) values with `pd.isna`.
*   **`class SmaStrategy(Strategy):`**: This defines our new strategy class named `SmaStrategy`. It inherits from the base `Strategy` class, meaning it will get all the foundational behaviors of a TradeMind strategy and we can override specific methods to implement our custom logic.

**2. The `initialize` Method:**
This method is called only once when the strategy is first loaded by the platform.
```python
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
        self.context.symbols = [self.parameters["symbol"]]

        self.context.log(f"SMA Crossover Strategy for {self.parameters['symbol']} initialized.")
```
*   **`self.parameters`**: A dictionary is created to hold all the configurable parameters for this strategy. This is a crucial practice because:
    *   It centralizes all tunable values (like symbol, SMA periods, trade size).
    *   It allows these parameters to be easily changed without altering the core logic, especially useful when using TradeMind's configuration files (`config.yaml`) or optimization tools, which can override these defaults.
*   **`self.context.symbols = [self.parameters["symbol"]]`**: This line is vital. It tells the TradeMind platform which financial instrument(s) this particular instance of the strategy should receive market data for. The platform will then ensure that the `on_bar` method (discussed next) is called with data for "AAPL" (or whatever symbol is specified).
*   **`self.context.log(...)`**: This demonstrates using the platform's logging facility. It's good practice to log key events, like initialization, for monitoring and debugging. The `Context` object provides this `log` method.

**3. The `on_bar` Method - Data Reception and Preparation:**
This method is the heart of the strategy, called every time a new bar of data arrives for any of the subscribed symbols.
```python
    def on_bar(self, context: Context, bar_dict: dict) -> None:
        """
        Called on every new bar of data for the subscribed symbols.
        Implement trading logic here.
        """
        symbol = self.parameters["symbol"]

        bars = bar_dict.get(symbol)
        if bars is None or 'close' not in bars or bars.empty:
            # self.context.log(f"No data or no 'close' column for {symbol}", level="WARNING")
            return

        if len(bars['close']) < self.parameters["slow_period"]:
            return
```
*   **`symbol = self.parameters["symbol"]`**: Retrieves the target symbol for convenience.
*   **`bars = bar_dict.get(symbol)`**: The `bar_dict` is a dictionary where keys are symbol strings and values are the corresponding bar data. This line attempts to get the data for our target symbol.
*   **Initial Data Checks**:
    *   `if bars is None or 'close' not in bars or bars.empty:`: This is a crucial sanity check. It ensures that data for the symbol actually exists in the `bar_dict`, that this data contains a 'close' price series (which is essential for SMA calculation), and that the data is not empty. If any of these conditions are true, the method returns early to avoid errors.
    *   `if len(bars['close']) < self.parameters["slow_period"]:`: This check ensures there's enough historical data to calculate the longest moving average (the `slow_period` SMA). If not, calculating the SMA would fail or produce incomplete results, so the method returns.

**4. The `on_bar` Method - Indicator Calculation and Validation:**
```python
        try:
            fast_ma_series = bars['close'].rolling(window=self.parameters["fast_period"]).mean()
            slow_ma_series = bars['close'].rolling(window=self.parameters["slow_period"]).mean()
        except Exception as e:
            # self.context.log(f"Error calculating MAs for {symbol}: {e}", level="ERROR")
            return

        if len(fast_ma_series) < 2 or len(slow_ma_series) < 2 or \
           pd.isna(fast_ma_series.iloc[-1]) or pd.isna(fast_ma_series.iloc[-2]) or \
           pd.isna(slow_ma_series.iloc[-1]) or pd.isna(slow_ma_series.iloc[-2]):
            return

        fast_ma_prev = fast_ma_series.iloc[-2]
        fast_ma_curr = fast_ma_series.iloc[-1]
        slow_ma_prev = slow_ma_series.iloc[-2]
        slow_ma_curr = slow_ma_series.iloc[-1]
```
*   **SMA Calculation**:
    *   `fast_ma_series = bars['close'].rolling(window=...).mean()`: This uses the pandas `rolling` method on the 'close' price series to calculate the moving average. `window` specifies the period.
    *   The `try-except` block is good practice for catching potential errors during calculation, although for simple rolling means it's less common unless data is malformed.
*   **MA Data Validation**:
    *   `if len(fast_ma_series) < 2 or ...`: After calculation, we need at least two values for each MA series (current and previous) to detect a crossover.
    *   `pd.isna(fast_ma_series.iloc[-1]) ...`: This checks if the latest (`.iloc[-1]`) or second-to-latest (`.iloc[-2]`) MA values are `NaN` (Not a Number). `NaN` values can occur at the beginning of a data series before enough data points are available for the rolling window. If any crucial MA value is `NaN`, we can't reliably detect a crossover, so we return.
*   **Storing MA Values**: The current and previous values for both fast and slow MAs are extracted for easier use in the logic.

**5. The `on_bar` Method - Position Check and Trading Logic:**
```python
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
*   **`position = context.get_position(symbol)`**: The `Context` object's `get_position` method is used to query the platform about the current holdings for the given `symbol`. This returns a `Position` object (or `None` if no position).
*   **`current_quantity = position.quantity if position else 0`**: Extracts the quantity from the position object. If there's no position, it defaults to 0.
*   **Buy Signal Logic**:
    *   `if fast_ma_prev <= slow_ma_prev and fast_ma_curr > slow_ma_curr:`: This is the core crossover condition. It checks if in the *previous* bar the fast MA was below or equal to the slow MA, AND in the *current* bar the fast MA is now above the slow MA. This signifies an upward crossover.
    *   `if current_quantity <= 0:`: This condition prevents placing a new buy order if the strategy is already long the asset (or if it's short, it would buy to cover and go long, depending on portfolio settings not covered here). It ensures we only buy if we are flat or short.
    *   `self.context.log(...)`: Logs the buy signal with relevant MA values and the timestamp from the bar data (`bars.index[-1]`).
    *   `context.buy(symbol, self.parameters["trade_size"])`: This is the action. It instructs the platform to execute a market buy order for the `symbol` with the specified `trade_size`.
*   **Sell Signal Logic (to close a long position)**:
    *   `elif fast_ma_prev >= slow_ma_prev and fast_ma_curr < slow_ma_curr:`: This checks for a downward crossover (fast MA was above or equal, now it's below).
    *   `if current_quantity > 0:`: This ensures we only sell if we are currently holding a long position. This logic is for closing an existing long position, not for initiating a short sale (though `context.sell` could be used for shorting if the platform and broker allow).
    *   `self.context.log(...)`: Logs the sell signal.
    *   `context.sell(symbol, self.parameters["trade_size"])`: Instructs the platform to execute a market sell order.

This breakdown covers the essential parts of the `SmaStrategy`. Each piece plays a role in receiving data, calculating indicators, making decisions, and interacting with the trading platform.

## 3. Using Your Strategy

Once you have saved this code (e.g., as `sma_strategy.py` in a directory known to TradeMind, perhaps configured in `config.yaml` under `strategy_engine.strategy_module_paths` as detailed in the [*TradeMind Configuration Guide*](Config_guide.md)):

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
    Refer to the [*TradeMind Configuration Guide*](Config_guide.md) for more details on `config.yaml`.

*   **Run TradeMind**: When the platform runs, it should load, initialize, and start feeding data to your `SmaStrategy` instance.

## 4. Important Considerations & Next Steps

*   **Order Types**: The example uses basic market orders (`context.buy`, `context.sell`). `pyquant` supports other order types like `OrderType.LIMIT`, `OrderType.STOP`, etc., which would require specifying a price in the order call. See the *TradeMind Python API Reference* for details.
*   **Position Sizing**: The `trade_size` is fixed. More advanced strategies use dynamic position sizing based on risk, volatility, or account equity.
*   **Risk Management**: While global risk limits are set in `config.yaml`, strategies can implement their own risk checks (e.g., stop-loss orders, max drawdown per strategy).
*   **Data Handling**: Understand precisely how `bar_dict` provides data (e.g., pandas DataFrame columns, data types).
*   **Backtesting**: Use `pyquant.BacktestEngine` to backtest this strategy and evaluate its profitability.
*   **Parameter Optimization**: `pyquant.StrategyOptimizer` allows for finding optimal strategy parameters.

Consult the [*TradeMind Python API Reference*](API_ref.md) for comprehensive details on all available functionalities.

## Conclusion

You've now seen the fundamental components of a Python trading strategy in TradeMind. This SMA crossover example provides a template for building more complex algorithms. The key is to understand the `initialize` and `on_bar` methods, how to use the `context` object, and how to process the `bar_dict` data.

Remember to thoroughly backtest and paper trade any strategy before deploying it with real capital.
