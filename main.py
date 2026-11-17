from flask import Flask
from plotlyGraph import plotly_stock_prices
from priceArray import getPriceArray
import plotly.graph_objs as go
import dash
from dash import dcc, html, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc
from rangeCalculator import calculate_candlestick_range
from priceRawData import saveInitialData, saveRealTimeData
from updateGraphComponents import updateComponents
import os

symbols = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "UK100", "HK50", "AUDUSD", "NZDUSD"]
timeframes = ["M5", "M15", "M30", "H1", "H4", "D1", "W1"]

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
    # 用呢個 Store 記住設定
    dcc.Store(id='settings-store', storage_type='local'),

    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,  # 5 秒
        n_intervals=0
    ),
    html.Div([
        html.Label("Symbol"),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[{'label': s, 'value': s} for s in symbols],
            value='XAUUSD',
            style={'width': '200px'}
        ),
        html.Label("Timeframe"),
        dcc.Dropdown(
            id='timeframe-dropdown',
            options=[{'label': t, 'value': t} for t in timeframes],
            value='M30',
            style={'width': '200px'}
        ),
        html.Label("Number of bars:"),
        dcc.Slider(
            id='graph-bars-slider',
            min=2, max=300, step=1, value=100,
            marks={i: str(i) for i in range(2, 301, 20)},
        ),
        html.Label("Graph Height:"),
        dcc.Slider(
            id='graph-height-slider',
            min=500, max=1500, step=50, value=900,
            marks={i: str(i) for i in range(500, 1501, 100)},
        ),
        html.Label("Graph Width:"),
        dcc.Slider(
            id='graph-width-slider',
            min=500, max=1500, step=10, value=900,
            marks={i: str(i) for i in range(500, 1501, 100)},
        )
    ], className='column'),
    html.Div([
        html.Div(id='slider-value-output'),
        html.Label("Threshold:"),
        dcc.Slider(
            id='my-slider',
            min=0, max=50, step=1, value=8,
            marks={i: str(i) for i in range(0, 51, 10)}
        ),
        html.Label("Graph Domain:"),
        dcc.Slider(
            id='graph-domain-slider',
            min=20, max=1200, step=10, value=50,
            marks={i: str(i) for i in range(20, 1201, 50)}
        )
    ], className='column')
], className='row', style={'width': '80%', 'margin': '0 auto'})


# ========== 儲存設定到 localStorage ==========
clientside_callback(
    """
    function(symbol, timeframe, bars, height, width, threshold, domain) {
        const settings = {
            symbol: symbol,
            timeframe: timeframe,
            bars: bars,
            height: height,
            width: width,
            threshold: threshold,
            domain: domain
        };
        localStorage.setItem('xau_dashboard_settings', JSON.stringify(settings));
        return settings;
    }
    """,
    Output('settings-store', 'data'),
    Input('symbol-dropdown', 'value'),
    Input('timeframe-dropdown', 'value'),
    Input('graph-bars-slider', 'value'),
    Input('graph-height-slider', 'value'),
    Input('graph-width-slider', 'value'),
    Input('my-slider', 'value'),
    Input('graph-domain-slider', 'value'),
    prevent_initial_call=True
)


# ========== 頁面載入時還原設定 ==========
clientside_callback(
    """
    function(n) {
        const saved = localStorage.getItem('xau_dashboard_settings');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                return null;
            }
        }
        return null;
    }
    """,
    Output('settings-store', 'data', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call='initial_duplicate'
)


# ========== 用還原嘅設定更新各個控制項 ==========
@dash_app.callback(
    Output('symbol-dropdown', 'value'),
    Output('timeframe-dropdown', 'value'),
    Output('graph-bars-slider', 'value'),
    Output('graph-height-slider', 'value'),
    Output('graph-width-slider', 'value'),
    Output('my-slider', 'value'),
    Output('graph-domain-slider', 'value'),
    Input('settings-store', 'data'),
    prevent_initial_call=True
)
def restore_settings(data):
    if not data:
        raise dash.exceptions.PreventUpdate
    return (
        data.get('symbol', 'XAUUSD'),
        data.get('timeframe', 'M30'),
        data.get('bars', 100),
        data.get('height', 900),
        data.get('width', 900),
        data.get('threshold', 8),
        data.get('domain', 50)
    )


@dash_app.callback(
    Output('live-update-graph', 'figure'),
    Output('my-slider', 'min'),
    Output('my-slider', 'max'),
    Output('graph-domain-slider', 'min'),
    Output('graph-domain-slider', 'max'),
    Output('graph-domain-slider', 'marks'),
    Output('my-slider', 'marks'),
    Output('slider-value-output', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('graph-height-slider', 'value'),
    Input('graph-width-slider', 'value'),
    Input('my-slider', 'value'),
    Input('symbol-dropdown', 'value'),
    Input('timeframe-dropdown', 'value'),
    Input('graph-domain-slider', 'value'),
    Input('graph-bars-slider', 'value')
)
def update_graph(n_intervals, graph_height, graph_width, value, symbol, timeframe, domain_value, bars):
    global counter, prevNumBars, prevTimeFrame

    folder_path = os.path.join(os.getcwd(), "data")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if counter == 0 or bars != prevNumBars or timeframe != prevTimeFrame:
        saveInitialData(bars, folder_path, symbol, timeframe)
        counter += 1
        prevNumBars = bars
        prevTimeFrame = timeframe
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
    interval = 1 if int(interval) == 0 else int(interval)
    tickvals = list(range(lowerBound, UpperBound + 1, interval))

    plotly_stock_prices(lowerBound, UpperBound, prices, domain, graph, value)

    graph.update_layout(
        title=symbol,
        xaxis=dict(
            range=[-domain, domain],
            tickmode='array',
            showgrid=False,
            tickvals=list(range(-domain, domain + 1, max(1, int((2 * domain) / 10))))
        ),
        yaxis=dict(
            range=[lowerBound - 10, UpperBound + 10],
            tickmode='array',
            showgrid=False,
            tickvals=tickvals
        ),
        yaxis2=dict(
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

    return (
        graph,
        threshold_min, threshold_max,
        domain_min, domain_max, domain_marks, threshold_marks,
        f"Threshold: {value}"
    )


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
