"""Charts for the S&P 500 Risk Lab."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from statsmodels.tsa.stattools import acf

COLORS = {
    "Rolling": "#7f7f7f",  # grey
    "EWMA": "#1f77b4",     # blue
    "GARCH": "#d62728",    # red
    "Index": "#2ca02c",    # green
    "Breach": "#d62728",
}

CRISES = {
    "2008 crisis": ("2008-09-01", "2009-06-30"),
    "COVID 2020": ("2020-02-15", "2020-06-30"),
    "2022 rate shock": ("2022-01-01", "2022-10-31"),
}


def _style(fig, title, height):
    """One look for every chart: white background, readable fonts, set height."""
    fig.update_layout(
        title=dict(text=title, x=0.01, xanchor="left"),
        template="plotly_white",
        height=height,
        font=dict(size=12),
        margin=dict(l=70, r=30, t=100, b=60),
    )
    fig.update_annotations(font_size=12, selector=dict(showarrow=False, yref="paper"))
    return fig


def shade_crises(fig, row=None, col=None, annotate=True):
    """Grey bands over the crisis periods, labelled along the band.

    For a single-panel figure call shade_crises(fig).
    For a figure made with make_subplots, pass the panel: row=1, col=1.
    Use annotate=False to skip the labels (for a second panel).
    """
    kwargs = {} if row is None else {"row": row, "col": col}
    for name, (start, end) in CRISES.items():
        if annotate:
            kwargs.update(annotation_text=name, annotation_position="top left",
                          annotation_textangle=-90,
                          annotation_font=dict(size=11, color="grey"))
        fig.add_vrect(x0=start, x1=end, fillcolor="grey", opacity=0.15,
                      line_width=0, **kwargs)
    return fig


def price_drawdown_chart(prices: pd.Series, ticker: str, title: str | None = None):
    """Chart 1. Top: price on a log scale. Bottom: distance below the previous peak.

    The log scale matters: with a normal scale, a stock that grew 300 times
    looks flat for most of its history. On a log scale, equal percentage
    moves look equal.
    """
    drawdown = prices / prices.cummax() - 1
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.65, 0.35], vertical_spacing=0.06)
    fig.add_trace(go.Scatter(x=prices.index, y=prices, name="Price",
                             line=dict(color=COLORS["EWMA"], width=1.5)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown, name="Drawdown",
                             fill="tozeroy", line=dict(color=COLORS["Breach"], width=1)),
                  row=2, col=1)
    shade_crises(fig, row=1, col=1)
    shade_crises(fig, row=2, col=1, annotate=False)
    fig.update_yaxes(title_text="Adjusted price (log scale)", type="log",
                     tickformat="~g", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown", tickformat=".0%", row=2, col=1)
    fig.update_xaxes(range=[prices.index[0], prices.index[-1]])
    fig.update_layout(showlegend=False)
    return _style(fig, title or f"{ticker}: price and drawdown", height=650)


def return_distribution_chart(returns: pd.Series, ticker: str,
                              title: str | None = None):
    """Chart 2. Left: histogram of returns with a normal curve on top.
    Right: QQ-plot against the normal distribution.
    """
    r = returns.dropna()
    mu, sigma = r.mean(), r.std()

    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.16,
                        subplot_titles=("Histogram<br>of daily returns",
                                        "QQ-plot<br>(against a normal)"))

    fig.add_trace(go.Histogram(x=r, histnorm="probability density", nbinsx=150,
                               name="Actual returns",
                               marker_color=COLORS["EWMA"], opacity=0.7),
                  row=1, col=1)
    grid = np.linspace(r.min(), r.max(), 400)
    fig.add_trace(go.Scatter(x=grid, y=stats.norm.pdf(grid, mu, sigma),
                             name="Normal curve",
                             line=dict(color=COLORS["Breach"], width=2)),
                  row=1, col=1)

    (osm, osr), (slope, intercept, _) = stats.probplot(r, dist="norm")
    fig.add_trace(go.Scatter(x=osm, y=osr, mode="markers", name="Returns",
                             marker=dict(color=COLORS["EWMA"], size=4)),
                  row=1, col=2)
    fig.add_trace(go.Scatter(x=[osm.min(), osm.max()],
                             y=[intercept + slope * osm.min(),
                                intercept + slope * osm.max()],
                             mode="lines", name="If returns were normal",
                             line=dict(color=COLORS["Breach"], dash="dash")),
                  row=1, col=2)

    fig.update_xaxes(title_text="Daily log return", tickformat=".0%",
                     nticks=5, tickangle=0, row=1, col=1)
    fig.update_yaxes(title_text="Density", row=1, col=1)
    fig.update_xaxes(title_text="Theoretical quantiles", nticks=5, row=1, col=2)
    fig.update_yaxes(title_text="Actual return", tickformat=".0%", row=1, col=2)
    fig.update_layout(legend=dict(orientation="h", y=-0.3, font=dict(size=11)))
    return _style(fig, title or f"{ticker}: are daily returns normal?", height=520)


def autocorrelation_chart(returns: pd.Series, ticker: str, nlags: int = 30,
                          title: str | None = None):
    """Chart 3. Autocorrelation of returns (left) next to squared returns (right).
    The dashed lines mark the range expected from pure noise (95%).
    """
    r = returns.dropna()
    lags = np.arange(1, nlags + 1)
    band = 1.96 / np.sqrt(len(r))

    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.08,
                        subplot_titles=("Returns<br>(can direction be predicted?)",
                                        "Squared returns<br>(do big moves cluster?)"))
    for col, series in enumerate([r, r ** 2], start=1):
        values = acf(series, nlags=nlags, fft=True)[1:]
        fig.add_trace(go.Bar(x=lags, y=values, marker_color=COLORS["EWMA"],
                             showlegend=False), row=1, col=col)
        for sign in (1, -1):
            fig.add_hline(y=sign * band, line_dash="dash", line_color="grey",
                          row=1, col=col)
        fig.update_xaxes(title_text="Lag (days)", row=1, col=col)
    fig.update_yaxes(title_text="Autocorrelation", row=1, col=1)
    return _style(fig, title or f"{ticker}: autocorrelation of returns", height=480)