import pandas as pd
import yfinance as yf


def get_prices(ticker: str, start: str = "2005-01-01") -> pd.Series:
    """Adjusted close prices for one ticker.

    Adjusted means splits and dividends are already built into the prices,
    which is what we need for correct returns.
    """
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data found for {ticker}")
    close = df["Close"]
    if isinstance(close, pd.DataFrame):  # newer yfinance returns a table
        close = close.iloc[:, 0]
    return close.dropna().rename(ticker)