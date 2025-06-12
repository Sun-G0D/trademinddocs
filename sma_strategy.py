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