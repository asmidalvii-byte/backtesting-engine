import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Backtesting Engine"

BLUE = "#7EC8E3"
PEACH = "#FFB347"
MINT = "#B5EAD7"
ROSE = "#FF9AA2"
BG = "#FFFAF7"
TEXT = "#3a3a3a"
FONT = "Times New Roman, serif"

NSE_STOCKS = [
    {"label": "Reliance", "value": "RELIANCE.NS"},
    {"label": "TCS", "value": "TCS.NS"},
    {"label": "Infosys", "value": "INFY.NS"},
    {"label": "HDFC Bank", "value": "HDFCBANK.NS"},
    {"label": "Nifty 50", "value": "^NSEI"},
]

app.layout = html.Div(style={"background": BG, "minHeight": "100vh", "fontFamily": FONT}, children=[

    # Navbar
    html.Div(style={
        "background": f"linear-gradient(90deg, {BLUE}, {PEACH})",
        "padding": "18px 32px",
        "borderRadius": "0 0 20px 20px",
        "marginBottom": "28px",
        "boxShadow": "0 4px 15px rgba(126,200,227,0.3)"
    }, children=[
        html.H1("Backtesting Engine", style={"color": "white", "margin": 0, "fontSize": "26px", "fontFamily": FONT}),
        html.P("Test trading strategies on NSE stocks in INR", style={"color": "rgba(255,255,255,0.85)", "margin": 0, "fontSize": "14px", "fontFamily": FONT})
    ]),

    dbc.Container(fluid=True, style={"padding": "0 32px"}, children=[
        dbc.Row([

            # Settings panel
            dbc.Col(width=3, children=[
                html.Div(style={"background": "white", "borderRadius": "16px", "padding": "24px", "boxShadow": "0 2px 12px rgba(0,0,0,0.07)"}, children=[

                    html.P("Stock", style={"fontSize": "11px", "fontWeight": "600", "color": "#aaa", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "4px", "fontFamily": FONT}),
                    dcc.Dropdown(id="ticker", options=NSE_STOCKS, value="RELIANCE.NS", clearable=False, style={"marginBottom": "16px", "fontFamily": FONT}),

                    html.P("Start date", style={"fontSize": "11px", "fontWeight": "600", "color": "#aaa", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "4px", "fontFamily": FONT}),
                    dcc.DatePickerSingle(id="start-date", date=date(2020, 1, 1), display_format="DD/MM/YYYY", style={"marginBottom": "16px", "width": "100%"}),

                    html.P("End date", style={"fontSize": "11px", "fontWeight": "600", "color": "#aaa", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "4px", "fontFamily": FONT}),
                    dcc.DatePickerSingle(id="end-date", date=date.today(), display_format="DD/MM/YYYY", style={"marginBottom": "16px", "width": "100%"}),

                    html.P("Initial capital (INR)", style={"fontSize": "11px", "fontWeight": "600", "color": "#aaa", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "4px", "fontFamily": FONT}),
                    dcc.Input(id="capital", type="number", value=100000, min=1000, step=1000, style={"borderRadius": "10px", "border": "1.5px solid #e0d8d0", "padding": "8px 12px", "fontSize": "13px", "width": "100%", "marginBottom": "16px", "fontFamily": FONT}),

                    html.P("Strategy", style={"fontSize": "11px", "fontWeight": "600", "color": "#aaa", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "4px", "fontFamily": FONT}),
                    dcc.Dropdown(id="strategy", options=[
                        {"label": "Moving Average Crossover", "value": "mac"},
                        {"label": "RSI Oversold/Overbought", "value": "rsi"}
                    ], value="mac", clearable=False, style={"marginBottom": "16px", "fontFamily": FONT}),

                    html.Div(id="strategy-params"),

                    html.Button("Run backtest", id="run-btn", n_clicks=0, style={
                        "background": f"linear-gradient(90deg, {BLUE}, {PEACH})",
                        "border": "none", "borderRadius": "12px", "color": "white",
                        "fontWeight": "600", "padding": "10px 0", "width": "100%",
                        "fontSize": "14px", "cursor": "pointer", "fontFamily": FONT,
                        "boxShadow": "0 4px 12px rgba(126,200,227,0.4)", "marginTop": "4px"
                    })
                ])
            ]),

            # Main content
            dbc.Col(width=9, children=[
                html.Div(id="metrics-row", style={"marginBottom": "16px"}),
                html.Div(style={"background": "white", "borderRadius": "16px", "padding": "20px", "boxShadow": "0 2px 12px rgba(0,0,0,0.07)", "marginBottom": "16px"}, children=[
                    html.P("Portfolio value over time", style={"fontWeight": "700", "fontSize": "15px", "color": TEXT, "fontFamily": FONT}),
                    dcc.Graph(id="portfolio-chart", style={"height": "280px"})
                ]),
                html.Div(style={"background": "white", "borderRadius": "16px", "padding": "20px", "boxShadow": "0 2px 12px rgba(0,0,0,0.07)", "marginBottom": "16px"}, children=[
                    html.P("Price chart with buy/sell signals", style={"fontWeight": "700", "fontSize": "15px", "color": TEXT, "fontFamily": FONT}),
                    dcc.Graph(id="price-chart", style={"height": "280px"})
                ]),
                html.Div(style={"background": "white", "borderRadius": "16px", "padding": "20px", "boxShadow": "0 2px 12px rgba(0,0,0,0.07)"}, children=[
                    html.P("Trade log", style={"fontWeight": "700", "fontSize": "15px", "color": TEXT, "fontFamily": FONT}),
                    html.Div(id="trade-table")
                ])
            ])
        ])
    ])
])

@app.callback(Output("strategy-params", "children"), Input("strategy", "value"))
def update_params(strategy):
    if strategy == "mac":
        return html.Div([
            html.P("Short MA", style={"fontSize": "11px", "color": "#aaa", "textTransform": "uppercase", "fontFamily": FONT}),
            dcc.Slider(id="param1", min=5, max=50, step=1, value=20, marks={5:"5", 20:"20", 50:"50"}, tooltip={"placement": "bottom"}),
            html.Br(),
            html.P("Long MA", style={"fontSize": "11px", "color": "#aaa", "textTransform": "uppercase", "fontFamily": FONT}),
            dcc.Slider(id="param2", min=20, max=200, step=5, value=50, marks={20:"20", 100:"100", 200:"200"}, tooltip={"placement": "bottom"}),
            html.Br()
        ])
    else:
        return html.Div([
            html.P("RSI period", style={"fontSize": "11px", "color": "#aaa", "textTransform": "uppercase", "fontFamily": FONT}),
            dcc.Slider(id="param1", min=7, max=30, step=1, value=14, marks={7:"7", 14:"14", 30:"30"}, tooltip={"placement": "bottom"}),
            html.Br(),
            html.P("Oversold threshold", style={"fontSize": "11px", "color": "#aaa", "textTransform": "uppercase", "fontFamily": FONT}),
            dcc.Slider(id="param2", min=20, max=50, step=1, value=35, marks={20:"20", 35:"35", 50:"50"}, tooltip={"placement": "bottom"}),
            html.Br()
        ])

@app.callback(
    Output("metrics-row", "children"),
    Output("portfolio-chart", "figure"),
    Output("price-chart", "figure"),
    Output("trade-table", "children"),
    Input("run-btn", "n_clicks"),
    State("ticker", "value"),
    State("start-date", "date"),
    State("end-date", "date"),
    State("capital", "value"),
    State("strategy", "value"),
    State("param1", "value"),
    State("param2", "value"),
    prevent_initial_call=False
)
def run_backtest(n, ticker, start, end, capital, strategy, param1, param2):
    empty = go.Figure().update_layout(paper_bgcolor=BG, plot_bgcolor=BG, margin=dict(t=10,b=10,l=10,r=10))

    try:
        raw = yf.Ticker(ticker).history(start=start, end=end)
        if raw.empty:
            return "", empty, empty, html.P("No data found.", style={"color": ROSE, "fontFamily": FONT})
    except:
        return "", empty, empty, html.P("Error fetching data.", style={"color": ROSE, "fontFamily": FONT})

    df = raw.copy()

    if strategy == "mac":
        df["short_ma"] = df["Close"].rolling(param1 or 20).mean()
        df["long_ma"] = df["Close"].rolling(param2 or 50).mean()
        df["signal"] = 0
        df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1
        df.loc[df["short_ma"] < df["long_ma"], "signal"] = -1
    else:
        delta = df["Close"].diff()
        avg_gain = delta.clip(lower=0).rolling(param1 or 14).mean()
        avg_loss = (-delta.clip(upper=0)).rolling(param1 or 14).mean()
        df["rsi"] = 100 - (100 / (1 + avg_gain / avg_loss))
        df["signal"] = 0
        df.loc[df["rsi"] < (param2 or 35), "signal"] = 1
        df.loc[df["rsi"] > (100 - (param2 or 35)), "signal"] = -1

    cap = float(capital)
    shares = 0
    trades = []
    pv = []
    buy_price = 0
    in_pos = False

    for i, row in df.iterrows():
        price = float(row["Close"])
        if row["signal"] == 1 and not in_pos and cap >= price:
            shares = cap / price
            buy_price = price
            cap = 0
            in_pos = True
            trades.append({"Date": str(i.date()), "Action": "BUY", "Price": f"₹{price:,.2f}", "Shares": round(shares, 4), "Value": f"₹{shares*price:,.2f}", "P&L": "—", "P&L %": "—"})
        elif row["signal"] == -1 and in_pos:
            cap = shares * price
            pnl = (price - buy_price) * shares
            trades.append({"Date": str(i.date()), "Action": "SELL", "Price": f"₹{price:,.2f}", "Shares": round(shares, 4), "Value": f"₹{cap:,.2f}", "P&L": f"₹{pnl:,.2f}", "P&L %": f"{((price-buy_price)/buy_price*100):.2f}%"})
            shares = 0
            in_pos = False
        pv.append({"Date": i, "Value": cap + shares * price})

    final = cap + shares * float(df["Close"].iloc[-1])
    df_pv = pd.DataFrame(pv)
    total_ret = ((final - float(capital)) / float(capital)) * 100
    daily_ret = df_pv["Value"].pct_change().dropna()
    sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252) if daily_ret.std() != 0 else 0
    max_dd = ((df_pv["Value"] - df_pv["Value"].cummax()) / df_pv["Value"].cummax() * 100).min()
    sells = [t for t in trades if t["Action"] == "SELL"]
    wins = [t for t in sells if float(t["P&L"].replace("₹","").replace(",","")) > 0]
    wr = (len(wins) / len(sells) * 100) if sells else 0

    metrics = dbc.Row([
        dbc.Col(html.Div(style={"background": bg, "borderRadius": "16px", "padding": "18px", "textAlign": "center", "boxShadow": "0 2px 10px rgba(0,0,0,0.06)"}, children=[
            html.P(label, style={"fontSize": "11px", "color": "#888", "textTransform": "uppercase", "margin": "0 0 4px", "fontFamily": FONT}),
            html.H3(val, style={"fontSize": "22px", "fontWeight": "700", "color": color, "margin": 0, "fontFamily": FONT})
        ]), width=True)
        for bg, color, val, label in [
            ("#E8F8F0", "#2ECC71", f"{total_ret:.2f}%", "Total Return"),
            ("#EAF4FB", BLUE, f"{sharpe:.2f}", "Sharpe Ratio"),
            ("#FFF0F0", ROSE, f"{max_dd:.2f}%", "Max Drawdown"),
            ("#FFF8EC", PEACH, f"{wr:.1f}%", "Win Rate"),
            ("#F5F0FF", "#9B8EC4", str(len(sells)), "Trades"),
        ]
    ])

    bh = float(capital) * (df["Close"] / float(df["Close"].iloc[0]))
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_pv["Date"], y=df_pv["Value"], name="Strategy", line=dict(color=BLUE, width=2.5), fill="tozeroy", fillcolor="rgba(126,200,227,0.1)"))
    fig1.add_trace(go.Scatter(x=df.index, y=bh, name="Buy & Hold", line=dict(color=PEACH, width=2, dash="dash")))
    fig1.update_layout(paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=TEXT),
                       xaxis=dict(showgrid=False, color="#aaa"), yaxis=dict(showgrid=True, gridcolor="#f0ebe6", tickprefix="₹"),
                       legend=dict(orientation="h", y=1.1), margin=dict(t=20,b=20,l=10,r=10))

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price", line=dict(color="#9B8EC4", width=1.8)))
    buys = [t for t in trades if t["Action"] == "BUY"]
    sels = [t for t in trades if t["Action"] == "SELL"]
    if buys:
        fig2.add_trace(go.Scatter(x=pd.to_datetime([t["Date"] for t in buys]),
                                   y=[float(t["Price"].replace("₹","").replace(",","")) for t in buys],
                                   mode="markers", name="Buy", marker=dict(color=MINT, size=12, symbol="triangle-up", line=dict(color="#2ECC71", width=1.5))))
    if sels:
        fig2.add_trace(go.Scatter(x=pd.to_datetime([t["Date"] for t in sels]),
                                   y=[float(t["Price"].replace("₹","").replace(",","")) for t in sels],
                                   mode="markers", name="Sell", marker=dict(color=ROSE, size=12, symbol="triangle-down", line=dict(color="#FF6B6B", width=1.5))))
    fig2.update_layout(paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=TEXT),
                       xaxis=dict(showgrid=False, color="#aaa"), yaxis=dict(showgrid=True, gridcolor="#f0ebe6", tickprefix="₹"),
                       legend=dict(orientation="h", y=1.1), margin=dict(t=20,b=20,l=10,r=10))

    table = dash_table.DataTable(
        data=pd.DataFrame(trades).to_dict("records"),
        columns=[{"name": c, "id": c} for c in pd.DataFrame(trades).columns],
        style_header={"background": "#FFF8F0", "fontWeight": "600", "color": TEXT, "fontSize": "12px", "border": "none", "fontFamily": FONT},
        style_cell={"fontSize": "13px", "color": TEXT, "padding": "10px 14px", "border": "none", "fontFamily": FONT},
        style_data_conditional=[
            {"if": {"filter_query": '{Action} = "BUY"', "column_id": "Action"}, "color": "#2ECC71", "fontWeight": "700"},
            {"if": {"filter_query": '{Action} = "SELL"', "column_id": "Action"}, "color": ROSE, "fontWeight": "700"},
            {"if": {"row_index": "odd"}, "background": "#FFFAF7"}
        ]
    ) if trades else html.P("No trades triggered.", style={"color": "#aaa", "fontFamily": FONT})

    return metrics, fig1, fig2, table

server = app.server

if __name__ == "__main__":
    app.run(debug=False)