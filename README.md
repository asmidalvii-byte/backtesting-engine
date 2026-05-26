# Backtesting Engine

A trading strategy backtesting tool built with Python and Dash, designed for NSE Indian stocks with INR pricing.

## What it does

- Test two strategies on any NSE stock — Moving Average Crossover and RSI Oversold/Overbought
- Adjustable parameters for each strategy using interactive sliders
- Performance metrics — Total Return, Sharpe Ratio, Max Drawdown, Win Rate
- Portfolio value chart comparing your strategy vs simply buying and holding
- Price chart with buy and sell signals marked
- Full trade log with entry/exit prices and P&L per trade

## Tech stack

Python · Dash · Plotly · yfinance · pandas · numpy

## Stocks available

Reliance · TCS · Infosys · HDFC Bank · Nifty 50

## How to run locally

```bash
pip install -r requirements.txt
python3 app.py
```

Then open `http://localhost:8050` in your browser.

## Live demo

https://backtesting-engine.onrender.com