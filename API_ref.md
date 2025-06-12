# TradeMind Python API Reference

## Introduction

This document provides an API reference for the `pyquant` library, the Python interface for developing, backtesting, and optimizing trading strategies within the TradeMind platform. It details the core classes, methods, and enumerations available to developers.

For tutorials and usage examples, please refer to the "Developing Your First Trading Strategy with TradeMind" guide.

## Table of Contents

*   [1. Core Strategy Classes](#1-core-strategy-classes)
    *   [1.1. `pyquant.Strategy`](#11-pyquantstrategy)
    *   [1.2. `pyquant.Context`](#12-pyquantcontext)
*   [2. Enumerations](#2-enumerations)
    *   [2.1. `pyquant.OrderSide`](#21-pyquantorderside)
    *   [2.2. `pyquant.OrderType`](#22-pyquantordertype)
    *   [2.3. `pyquant.Timeframe`](#23-pyquanttimeframe)
*   [3. Backtesting](#3-backtesting)
    *   [3.1. `pyquant.BacktestEngine`](#31-pyquantbacktestengine)
    *   [3.2. `pyquant.BacktestVisualizer`](#32-pyquantbacktestvisualizer)
*   [4. Optimization](#4-optimization)
    *   [4.1. `pyquant.StrategyOptimizer`](#41-pyquantstrategyoptimizer)
*   [5. Data Structures](#5-data-structures)
    *   [5.1. Position Object](#51-position-object)
    *   [5.2. Bar Data Format (in \`bar_dict\`)](#52-bar-data-format-in-bar_dict)
    *   [5.3. OrderTicket Object](#53-orderticket-object)
    *   [5.4. BacktestResults Object](#54-backtestresults-object)
    *   [5.5. BestParams Object](#55-bestparams-object)

---

## 1. Core Strategy Classes

### 1.1. `pyquant.Strategy`

The base class for all trading strategies implemented in TradeMind. Users must subclass `Strategy` and override its methods to define custom trading logic.

#### Methods to Override:

##### `initialize(self) -> None`
*   **Description:** Called once when the strategy instance is created and initialized by the platform. Use this method to set strategy parameters, define symbols to trade, initialize indicators, or perform any other one-time setup tasks.
*   **Parameters:** None.
*   **Returns:** None.
*   **Example:**
    ```python
    from pyquant import Strategy, Context

    class MyStrategy(Strategy):
        def initialize(self) -> None:
            self.parameters = {"symbol": "AAPL", "period": 20}
            # Assuming self.context is automatically available or passed if needed
            # self.context.symbols = [self.parameters["symbol"]] # Set in platform based on config
            self.sma = [] # Example placeholder for an indicator
            # self.context.log("MyStrategy initialized.") # Use context for logging
    ```

##### `on_bar(self, context: Context, bar_dict: dict) -> None`
*   **Description:** Called for each new market data bar received for the symbols the strategy is subscribed to (via `context.symbols` which are typically set based on strategy configuration). This is the primary method for implementing trading logic, signal generation, and order placement.
*   **Parameters:**
    *   `context` (`Context`): The strategy execution context object, providing access to portfolio information, order functions, and other platform interactions.
    *   `bar_dict` (`dict`): A dictionary where keys are symbol strings (e.g., "AAPL") and values are the corresponding bar data (typically a pandas DataFrame with OHLCV data). See [Bar Data Format](#52-bar-data-format-in-bar_dict).
*   **Returns:** None.
*   **Example:**
    ```python
    def on_bar(self, context: Context, bar_dict: dict) -> None:
        if "AAPL" in bar_dict:
            aapl_bars = bar_dict["AAPL"]
            if not aapl_bars.empty:
                current_close = aapl_bars['close'].iloc[-1]
                # ... trading logic ...
        else:
            context.log("AAPL data not in bar_dict for current bar.", level="WARNING")

    ```

### 1.2. `pyquant.Context`

An object provided to strategy methods (`on_bar`, `on_tick`, etc.) that allows the strategy to interact with the trading platform and access contextual information.

#### Attributes (Read-only for strategy logic):

##### `symbols: list[str]`
*   **Description:** A list of symbol strings that the current strategy instance is configured to operate on. This is typically set by the platform based on the strategy's configuration in `config.yaml`.
*   **Type:** `list[str]`

#### Methods:

##### `get_position(self, symbol: str) -> Position | None`
*   **Description:** Retrieves the current position information for the specified symbol held by this strategy.
*   **Parameters:**
    *   `symbol` (`str`): The trading symbol (e.g., "AAPL").
*   **Returns:** A `Position` object (see [Position Object](#51-position-object)) containing details of the position if one exists, otherwise `None` or a `Position` object with zero quantity.

##### `buy(self, symbol: str, quantity: float, price: float | None = None, order_type: OrderType = OrderType.MARKET, **kwargs) -> OrderTicket | None`
*   **Description:** Submits a buy order for the specified symbol.
*   **Parameters:**
    *   `symbol` (`str`): The trading symbol.
    *   `quantity` (`float`): The number of shares/contracts to buy. Must be positive.
    *   `price` (`float | None`, optional): The limit price for `OrderType.LIMIT` or `OrderType.STOP_LIMIT` orders. Defaults to `None` for market orders.
    *   `order_type` (`OrderType`, optional): The type of order to place. Defaults to `OrderType.MARKET`. See [OrderType](#22-pyquantordertype).
    *   `**kwargs`: Additional order parameters (e.g., `time_in_force: str`, `stop_price: float` for stop orders).
*   **Returns:** An `OrderTicket` object (see [OrderTicket Object](#53-orderticket-object)) representing the submitted order, or `None` if submission failed.

##### `sell(self, symbol: str, quantity: float, price: float | None = None, order_type: OrderType = OrderType.MARKET, **kwargs) -> OrderTicket | None`
*   **Description:** Submits a sell order for the specified symbol. Can be used to close a long position or open a short position (if supported).
*   **Parameters:** (Same as `buy`, but `quantity` is for selling. Ensure `quantity` is positive.)
*   **Returns:** An `OrderTicket` object or `None`.

##### `cancel_order(self, order_id: str) -> bool`
*   **Description:** Attempts to cancel an open order.
*   **Parameters:**
    *   `order_id` (`str`): The ID of the order to cancel (obtained from an `OrderTicket` object).
*   **Returns:** `True` if the cancel request was accepted by the platform, `False` otherwise. (Actual cancellation confirmation depends on exchange response).

##### `log(self, message: str, level: str = "INFO") -> None`
*   **Description:** Logs a message from the strategy using the platform's logging facility.
*   **Parameters:**
    *   `message` (`str`): The message to log.
    *   `level` (`str`, optional): Log level (e.g., `"INFO"`, `"DEBUG"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`). Defaults to `"INFO"`.
*   **Returns:** None.

---

## 2. Enumerations

### 2.1. `pyquant.OrderSide`
Specifies the side of an order.
*   `OrderSide.BUY`
*   `OrderSide.SELL`

### 2.2. `pyquant.OrderType`
Specifies the type of an order.
*   `OrderType.MARKET`: Market order.
*   `OrderType.LIMIT`: Limit order.
*   `OrderType.STOP`: Stop order (becomes a market order when triggered).
*   `OrderType.STOP_LIMIT`: Stop-limit order (becomes a limit order when triggered).

### 2.3. `pyquant.Timeframe`
Specifies the timeframe or resolution of bar data.
*   `Timeframe.M1`: 1 Minute
*   `Timeframe.M5`: 5 Minutes
*   `Timeframe.H1`: 1 Hour
*   `Timeframe.D1`: 1 Day
*   *(Other common timeframes like `S1`, `M15`, `M30`, `W1`, `MN1` might also be supported)*

---

## 3. Backtesting

### 3.1. `pyquant.BacktestEngine`
Class used to run historical backtests of strategies.

#### Methods:

##### `__init__(self, initial_capital: float = 100000.0, commission_model: CommissionModel | None = None, slippage_model: SlippageModel | None = None, cash_instrument: str = "USD", risk_free_rate: float = 0.0, log_level: str = "INFO", **kwargs) -> None`
*   **Description:** Initializes the backtest engine with various settings that define the simulation environment.
*   **Parameters:**
    *   `initial_capital` (`float`, optional): The starting cash balance for the backtest portfolio. Default: `100000.0`.
    *   `commission_model` (`CommissionModel | None`, optional): An object defining how trading commissions are calculated. If `None`, no commissions are applied.
        *   Example common implementations: `FixedPerTradeCommission(cost_per_trade: float)`, `PercentageCommission(percentage: float)`, `PerShareCommission(cost_per_share: float)`.
    *   `slippage_model` (`SlippageModel | None`, optional): An object defining how trade execution slippage is simulated. If `None`, trades execute ideally.
        *   Example common implementations: `FixedSlippage(slippage_per_trade: float)`, `PercentageSlippage(slippage_percentage: float)`, `VolumeShareSlippage(...)`.
    *   `cash_instrument` (`str`, optional): The currency symbol representing cash in the portfolio. Default: `"USD"`.
    *   `risk_free_rate` (`float`, optional): The annualized risk-free rate for metrics like Sharpe Ratio (decimal, e.g., `0.02` for 2%). Default: `0.0`.
    *   `log_level` (`str`, optional): Logging verbosity for the engine. Default: `"INFO"`.
    *   `**kwargs`: Other engine settings like `default_data_path: str`, `default_order_type: OrderType`, `max_lookback_data_needed: int`, `data_loader_config: dict`, `performance_tracker_config: dict`.
*   **Returns:** None.
*   **Example:**
    ```python
    from pyquant import BacktestEngine
    # from pyquant.commission import FixedPerTradeCommission
    # from pyquant.slippage import PercentageSlippage

    # commission = FixedPerTradeCommission(cost_per_trade=1.0)
    # slippage = PercentageSlippage(slippage_percentage=0.0005) # 0.05%

    backtest_engine = BacktestEngine(
        initial_capital=50000.0,
        # commission_model=commission,
        # slippage_model=slippage,
        risk_free_rate=0.01 # 1% annualized
    )
    ```

##### `add_strategy(self, strategy: Strategy, name: str | None = None) -> None`
*   **Description:** Adds a strategy instance to be run in the backtest.
*   **Parameters:**
    *   `strategy` (`Strategy`): An instantiated strategy object.
    *   `name` (`str | None`, optional): A unique name for this strategy instance in the backtest, useful if running multiple strategies.
*   **Returns:** None.

##### `add_bar_data(self, symbol: str, timeframe: Timeframe, data: pd.DataFrame, data_name: str | None = None) -> None`
*   **Description:** Adds historical bar data for a specific symbol and timeframe.
*   **Parameters:**
    *   `symbol` (`str`): The symbol for which the data is being added.
    *   `timeframe` (`Timeframe`): The timeframe of the bar data.
    *   `data` (`pd.DataFrame`): A pandas DataFrame. See [Bar Data Format](#52-bar-data-format-in-bar_dict).
    *   `data_name` (`str | None`, optional): A name for this data feed, if needed.
*   **Returns:** None.

##### `run(self, start_time, end_time, initial_capital: float | None = None, **kwargs) -> BacktestResults`
*   **Description:** Executes the backtest over the specified time range.
*   **Parameters:**
    *   `start_time`: The start datetime (or string interpretable as datetime) for the backtest period.
    *   `end_time`: The end datetime for the backtest period.
    *   `initial_capital` (`float | None`, optional): Overrides `initial_capital` from `__init__` if provided.
    *   `**kwargs`: Other backtest execution parameters.
*   **Returns:** `BacktestResults` object. See [BacktestResults Object](#54-backtestresults-object).

### 3.2. `pyquant.BacktestVisualizer`
Class used to generate reports or plots from backtest results.

#### Methods:

##### `generate_report(self, results: BacktestResults, output_path: str | None = None, show_plot: bool = True) -> None`
*   **Description:** Generates a performance report from backtest results. Can display plots and/or save to a file (e.g., HTML).
*   **Parameters:**
    *   `results` (`BacktestResults`): The result object from `BacktestEngine.run()`.
    *   `output_path` (`str | None`, optional): File path to save the report (e.g., `report.html`). If `None`, report might only be displayed.
    *   `show_plot` (`bool`, optional): Whether to display plots interactively (if applicable). Default: `True`.
*   **Returns:** None.
*   **Example Output:** (Conceptual)
    *   [Image of a backtest performance report plot, showing equity curve, drawdowns, trades, and performance metrics table]

---

## 4. Optimization

### 4.1. `pyquant.StrategyOptimizer`
Class used to perform parameter optimization for strategies by running multiple backtests.

#### Methods:

##### `__init__(self, strategy_class: type[Strategy], backtest_engine_settings: dict | None = None, **kwargs)`
*   **Description:** Initializes the optimizer with the strategy class (not an instance) and settings for the underlying backtests.
*   **Parameters:**
    *   `strategy_class` (`type[Strategy]`): The class of the strategy to optimize (e.g., `SmaStrategy`, not `SmaStrategy()`).
    *   `backtest_engine_settings` (`dict | None`, optional): A dictionary of settings to pass to the `BacktestEngine` for each optimization run (e.g., `initial_capital`, `commission_model`).
    *   `**kwargs`: Other optimizer-specific settings (e.g., `parallelization_method`).
*   **Returns:** None.

##### `add_bar_data(self, symbol: str, timeframe: Timeframe, data: pd.DataFrame, data_name: str | None = None) -> None`
*   **Description:** Adds historical bar data for optimization runs.
*   **Parameters:** Same as `BacktestEngine.add_bar_data`.
*   **Returns:** None.

##### `grid_search(self, param_grid: dict, start_time, end_time, optimize_metric: str, higher_is_better: bool = True, **kwargs) -> BestParams`
*   **Description:** Performs a grid search over specified parameter ranges to find the set that optimizes the `optimize_metric`.
*   **Parameters:**
    *   `param_grid` (`dict`): Keys are parameter names (strings from `Strategy.parameters`), values are lists/iterables of values to test.
        *   Example: `{"fast_period": [5, 10, 15], "slow_period": [20, 30, 40]}`
    *   `start_time`: Start datetime for the optimization period.
    *   `end_time`: End datetime for the optimization period.
    *   `optimize_metric` (`str`): Name of the performance metric to optimize (e.g., `'sharpe_ratio'`, `'total_return'`, `'max_drawdown'`).
    *   `higher_is_better` (`bool`, optional): Whether a higher value of `optimize_metric` is better. Default: `True`.
    *   `**kwargs`: Additional parameters for each backtest run.
*   **Returns:** `BestParams` object. See [BestParams Object](#55-bestparams-object).

---

## 5. Data Structures

### 5.1. Position Object
Represents a strategy's current holding in a particular symbol. (Returned by `Context.get_position()`).

#### Attributes:
*   `symbol` (`str`): The symbol of the position.
*   `quantity` (`float`): Number of shares/contracts. Positive for long, negative for short, zero for flat.
*   `average_price` (`float`): Average entry price of the current position.
*   `unrealized_pnl` (`float`): Current unrealized profit or loss.
*   `realized_pnl` (`float`): Realized profit or loss for this symbol during the strategy's lifetime or a defined period.
*   `last_sale_price` (`float`): The price at which the PnL was last calculated.
*   `cost_basis` (`float`): Total cost of the current open position.

### 5.2. Bar Data Format (in `bar_dict`)
The data provided for each symbol in the `bar_dict` argument of `Strategy.on_bar`. Typically a pandas DataFrame.

#### DataFrame Structure:
*   **Index:** `DatetimeIndex` (timestamps of the bars, localized to exchange timezone or UTC).
*   **Columns (Standard):**
    *   `open`: (`float`) Opening price of the bar.
    *   `high`: (`float`) Highest price during the bar.
    *   `low`: (`float`) Lowest price during the bar.
    *   `close`: (`float`) Closing price of the bar.
    *   `volume`: (`float` or `int`) Trading volume during the bar.
*   *(Additional columns like `vwap`, `trades` might be present depending on the data source).*

### 5.3. OrderTicket Object
Represents an order that has been submitted to the platform. (Returned by `Context.buy()` and `Context.sell()`).

#### Attributes (Examples):
*   `order_id` (`str`): Unique identifier for the order.
*   `symbol` (`str`): Symbol of the order.
*   `quantity` (`float`): Ordered quantity.
*   `side` (`OrderSide`): Buy or Sell.
*   `order_type` (`OrderType`): Market, Limit, etc.
*   `limit_price` (`float | None`): Limit price if applicable.
*   `status` (`str`): Current status of the order (e.g., "Submitted", "Accepted", "Filled", "Cancelled", "Rejected").
*   `filled_quantity` (`float`): Quantity filled.
*   `average_fill_price` (`float | None`): Average price at which the order was filled.
*   `created_timestamp`: Timestamp of order creation.
*   `last_update_timestamp`: Timestamp of last status update.

### 5.4. BacktestResults Object
Contains the results and performance metrics from a backtest run. (Returned by `BacktestEngine.run()`).

#### Attributes/Methods (Examples):
*   `portfolio_history` (`pd.DataFrame`): Timeseries of portfolio value, cash, PnL.
*   `trade_log` (`list[dict]` or `pd.DataFrame`): Record of all trades executed.
*   `performance_metrics` (`dict`): Key metrics like:
    *   `total_return` (`float`)
    *   `sharpe_ratio` (`float`)
    *   `max_drawdown` (`float`)
    *   `sortino_ratio` (`float`)
    *   `win_rate` (`float`)
    *   `profit_factor` (`float`)
    *   `total_trades` (`int`)
*   `equity_curve` (`pd.Series`): Timeseries of portfolio equity.
*   `get_metric(name: str) -> float | None`: Method to retrieve a specific metric.

### 5.5. BestParams Object
Contains the best parameter set and corresponding metric value from an optimization run. (Returned by `StrategyOptimizer.grid_search()`).

#### Attributes (Examples):
*   `best_parameters` (`dict`): The dictionary of parameters that yielded the best metric.
*   `best_metric_value` (`float`): The value of the `optimize_metric` for the `best_parameters`.
*   `optimization_summary` (`pd.DataFrame` or `list[dict]`): A summary of all parameter combinations tested and their metric values.
