from flask import Flask, render_template
from plotlyGraph import plotly_stock_prices
from priceArray import getPriceArray
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
from rangeCalculator import calculate_candlestick_range
from priceRawData import saveInitialData, saveRealTimeData
from updateGraphComponents import updateComponents
import os

symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "UK100", "HK50", "AUDUSD", "NZDUSD"]
timeframes = ["M5", "M15", "M30", "H1", "H4", "D1", "W1"]

slider_value = 5
min_value = 0
max_value = 50
default_value = 8
counter = 0
prevNumBars = 100
prevTimeFrame = 'M30'

app = Flask(__name__)

dash_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/XAU/',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

dash_app.layout = html.Div([
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 5000,
        n_intervals=0
    ),
    html.Div([
        html.Label("Symbol"),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': symbol, 'value': symbol} for symbol in symbols],
            value=symbols[0],
            style={'width': '200px'}
        ),
        html.Label("Timeframe"),
        dcc.Dropdown(
            id='timeframe-dropdown',
            options=[{'label': timeframe, 'value': timeframe} for timeframe in timeframes],
            value=timeframes[2],
            style={'width': '200px'}
        ),
        html.Label("Number of bars:"),
        dcc.Slider(
            id='graph-bars-slider',
            min=2,
            max=300,
            step=1,
            value=100,
            marks={i: str(i) for i in range(2, 300, 20)},
        ),
        html.Label("Graph Height:"),
        dcc.Slider(
            id='graph-height-slider',
            min=500,
            max=1500,
            step=50,
            value=900,
            marks={i: str(i) for i in range(500, 1500, 50)},
        ),
        html.Label("Graph Width:"),
        dcc.Slider(
            id='graph-width-slider',
            min=500,
            max=1500,
            step=10,
            value=900,
            marks={i: str(i) for i in range(500, 1501, 100)}
        )
    ], className='column'),
    html.Div([
        html.Div(id='graph-container'),
        html.Div(id='slider-value-output'),
        dcc.Slider(
            id='my-slider',
            min=0,
            max=50,
            step=1,
            value=8,
            marks={i: str(i) for i in range(0, 50, 10)}
        ),
        html.Label("Graph Domain:"),
        dcc.Slider(
            id='graph-domain-slider',
            min=20,
            max=1200,
            step=10,
            value=50,
            marks={i: str(i) for i in range(20, 1200, 50)}
        )
    ], className='column')
], className='row', style={'width': '80%', 'margin': '0 auto'})


@dash_app.callback(
    Output('live-update-graph', 'figure'),
    Output('my-slider', 'min'),
    Output('my-slider', 'max'),
    Output('graph-domain-slider', 'min'),
    Output('graph-domain-slider', 'max'),
    Output('graph-domain-slider', 'marks'),
    Output('my-slider', 'marks'),
    Output('slider-value-output', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('graph-height-slider', 'value'),
     Input('graph-width-slider', 'value'),
     Input('my-slider', 'value'),
     Input('symbol-dropdown', 'value'),
     Input('timeframe-dropdown', 'value'),
     Input('graph-domain-slider', 'value'),
     Input('graph-bars-slider', 'value')]
)
def update_graph(n_intervals, graph_height, graph_width, value, symbol, timeframe, domain_value, bars):
    folder_name = "data"
    folder_path = os.path.join(os.getcwd(), folder_name)

    global counter
    global prevNumBars
    global prevTimeFrame

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if counter == 0 or bars != prevNumBars or timeframe != prevTimeFrame:
        saveInitialData(bars, folder_path, symbol, timeframe)
        counter = counter + 1
        prevNumBars = bars
        prevTimeFrame = timeframe
        print(counter, prevNumBars, prevTimeFrame)
    else:
        saveRealTimeData(folder_path, symbol, timeframe)

    graph = go.Figure()
    prices = getPriceArray(symbol, timeframe, bars)

    if not prices or len(prices) < 8:
        empty_fig = go.Figure()
        empty_fig.update_layout(title=f"{symbol} - No data available")
        return empty_fig, 0, 50, 20, 200, {}, {}, "No data from API"

    max_range, data_range, mean_range, std_range, iqr = calculate_candlestick_range(prices)

    domain = domain_value
    lowerBound = round(prices[0] - data_range)
    UpperBound = round(prices[0] + data_range)

    interval = (UpperBound - lowerBound) / 10
    if int(interval) == 0:
        interval = 1
    else:
        interval = int(interval)

    tickvals = list(range(lowerBound, UpperBound + 1, interval))
    threshold = value
    plotly_stock_prices(lowerBound, UpperBound, prices, domain, graph, threshold)

    graph.update_layout(
        title=symbol,
        xaxis=dict(
            range=[-domain, domain],
            tickmode='array',
            showgrid=False,
            tickvals=list(range(-domain, domain + 1, int((2 * domain) / 10) if domain > 0 else 1))
        ),
        yaxis=dict(
            range=[lowerBound - 10, UpperBound + 10],
            tickmode='array',
            showgrid=False,
            tickvals=tickvals
        ),
        yaxis2=dict(
            title='',
            showline=True,
            showgrid=False,
            range=[-max(abs(lowerBound), abs(UpperBound)), max(abs(lowerBound), abs(UpperBound))],
            tickvals=tickvals,
            tickcolor='grey',
            anchor='x',
            overlaying='y',
            side='left'
        ),
        showlegend=True,
        height=graph_height,
        width=graph_width
    )

    threshold_min, threshold_max, domain_min, domain_max, domain_marks, threshold_marks = updateComponents(symbol)

    if symbol in symbols:
        return graph, threshold_min, threshold_max, domain_min, domain_max, domain_marks, threshold_marks, f"Threshold:: {value}"
    else:
        return graph, 0, 100, 20, 100, {}, {}, f"Threshold:: {value}"


@app.route('/XAU')
def XAU():
    return dash_app.index()

@app.route('/')
def index():
    return '''
    <h1>XAU Dashboard</h1>
    <p><a href="/XAU/">Click here to open the live chart</a></p>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)