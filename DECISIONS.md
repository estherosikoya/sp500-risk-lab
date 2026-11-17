# Decisions

A log of the choices I made in this project, what I rejected, and why.
## 1. Market: S&P 500
**Date:** 2026-11-14
**Decision:** Build the first version on S&P 500 stocks.
**Why:** Clean, widely available data, a clear benchmark (the index itself).
**Rejected:** FTSE MIB (smaller universe, patchier data) and the Nigerian Exchange (free data is limited). Either could be a second market in a later version.

## 2. Time-series splits are by date, never by percentage
**Date:** 2026-11-14
**Decision:** All testing uses walk-forward folds defined by calendar dates. No random splits and no single 80/20 split.
**Why:** One percentage split gives one test period, which could be calm or a crash. Many yearly folds show how each model behaves across different market conditions.

## 3. Holdout period starts 2024-01-01
**Date:** 2026-11-17
**Decision:** Data from 2024-01-01 onward is not used until the final evaluation. It is used once.
**Why:** It gives an honest test on data the models never influenced. This date was chosen before any modelling.

## 4. Free tools only
**Date:** 2026-11-14
**Decision:** Use only tools that need no payment card: GitHub, GitHub Actions, GitHub Container Registry, Streamlit Community Cloud and Docker for personal use.
**Why:** This is a learning and portfolio project, and I don't want to spend money on it.
**Rejected:** Google Cloud, AWS and Azure. Their free tiers need a billing account with a payment method.