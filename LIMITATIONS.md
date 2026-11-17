# Limitations

What this project cannot do, and where its results should be read with care. I add to this file whenever I find a new weakness.

## 1. Survivorship bias
**What:** I use today's S&P 500 members. Companies that left the index, for example through bankruptcy or a takeover, are missing.
**Effect:** Historical results look better than reality, and tail risk is understated.
**Status:** Cannot be fixed with free data.

## 2. Data source
**What:** Prices come from Yahoo Finance through the `yfinance` package.
**Effect:** Fine for learning, but not licensed or reliable enough for production use.
**Status:** A production version would use a licensed data vendor.