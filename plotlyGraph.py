import plotly.graph_objs as go

def plotly_stock_prices(min_val, max_val, prices, domain, graph, threshold):
    if not prices or len(prices) < 2:
        return

    midpoint = (min_val + max_val) / 2
    prev_direction = ''
    previousY = prices[0]
    x_coordinate = 0.0
    intermediate_x = 0.0
    intermediate_y = 0.0

    # 收集所有線段座標（大幅減少 trace 數量）
    line_x = []
    line_y = []
    marker_x = []
    marker_y = []

    interval = max(1, int((max_val - min_val) / 10))

    # 畫 45 度網格（保留原本視覺）
    for i in range(20):
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint - domain + interval * (i + 1),
            x1=domain, y1=midpoint + domain + interval * (i + 1),
            line=dict(color="rgba(214, 219, 223, 0.4)", width=1)
        )
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint - domain - interval * (i + 1),
            x1=domain, y1=midpoint + domain - interval * (i + 1),
            line=dict(color="rgba(214, 219, 223, 0.4)", width=1)
        )
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint + domain - interval * i,
            x1=domain, y1=midpoint - domain - interval * i,
            line=dict(color="rgba(214, 219, 223, 0.4)", width=1)
        )
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint + domain + interval * (i + 1),
            x1=domain, y1=midpoint - domain + interval * (i + 1),
            line=dict(color="rgba(214, 219, 223, 0.4)", width=1)
        )

    # 起點
    line_x.append(0)
    line_y.append(midpoint)
    marker_x.append(0)
    marker_y.append(midpoint)

    for i in range(1, len(prices)):
        difference = prices[i] - previousY
        current_y = (previousY + midpoint + x_coordinate) / 2
        direction = 'up' if difference > 0 else 'down'

        if direction == prev_direction or i == 1 or prev_direction == '':
            if (prices[i] > current_y and direction == 'down') or (prices[i] < current_y and direction == 'up'):
                intermediate_x = x_coordinate - difference
                if prices[i] < current_y and direction == 'up':
                    intermediate_x = x_coordinate - difference
                elif prices[i] < current_y and direction == 'down':
                    intermediate_x = x_coordinate
                elif prices[i] > current_y and direction == 'up':
                    intermediate_x = x_coordinate
                elif prices[i] > current_y and direction == 'down':
                    intermediate_x = x_coordinate - difference
                intermediate_y = prices[i]

                line_x.extend([x_coordinate, intermediate_x])
                line_y.extend([previousY, intermediate_y])
                previousY = intermediate_y
                x_coordinate = intermediate_x
            else:
                if (previousY < current_y and direction == 'down') or (previousY > current_y and direction == 'up'):
                    intermediate_x = x_coordinate
                else:
                    if (prices[i] > current_y and previousY < current_y) or (prices[i] < current_y and previousY > current_y):
                        if x_coordinate == 0:
                            intermediate_y = (midpoint + previousY) / 2
                            intermediate_x = intermediate_y - midpoint
                        else:
                            referenceC = previousY + x_coordinate
                            intermediate_y = (referenceC + midpoint) / 2
                            intermediate_x = intermediate_y - midpoint

                        line_x.extend([x_coordinate, intermediate_x])
                        line_y.extend([previousY, intermediate_y])
                        if intermediate_y != min_val:
                            marker_x.append(intermediate_x)
                            marker_y.append(prices[i])
                            x_coordinate = intermediate_x
                    else:
                        if prices[i] <= current_y and direction == 'up':
                            intermediate_x = x_coordinate - difference
                        elif prices[i] <= current_y and direction == 'down':
                            intermediate_x = x_coordinate
                        elif prices[i] >= current_y and direction == 'up':
                            intermediate_x = x_coordinate
                        elif prices[i] >= current_y and direction == 'down':
                            intermediate_x = x_coordinate - difference
                        intermediate_y = prices[i]

                        line_x.extend([x_coordinate, intermediate_x])
                        line_y.extend([previousY, intermediate_y])

                line_x.extend([intermediate_x, intermediate_x])
                line_y.extend([intermediate_y, prices[i]])
                marker_x.append(0)
                marker_y.append(midpoint)
                x_coordinate = intermediate_x
                prev_direction = direction

            marker_x.append(intermediate_x)
            marker_y.append(prices[i])
            line_x.extend([x_coordinate, intermediate_x])
            line_y.extend([intermediate_y, prices[i]])
            prev_direction = direction
            x_coordinate = intermediate_x
            previousY = prices[i]
        else:
            if abs(difference) >= threshold:
                if (prices[i] > current_y and previousY < current_y) or (previousY < current_y and previousY > current_y) or (prices[i] < current_y and previousY > current_y):
                    if x_coordinate == 0:
                        intermediate_y = (midpoint + previousY) / 2
                        intermediate_x = intermediate_y - midpoint
                    else:
                        referenceC = previousY + x_coordinate
                        intermediate_y = (referenceC + midpoint) / 2
                        intermediate_x = intermediate_y - midpoint

                    line_x.extend([x_coordinate, intermediate_x])
                    line_y.extend([previousY, intermediate_y])
                    if intermediate_y != min_val:
                        marker_x.append(intermediate_x)
                        marker_y.append(prices[i])
                else:
                    if prices[i] < current_y and direction == 'up':
                        intermediate_x = x_coordinate - difference
                    elif prices[i] < current_y and direction == 'down':
                        intermediate_x = x_coordinate
                    elif prices[i] > current_y and direction == 'up':
                        intermediate_x = x_coordinate
                    elif prices[i] > current_y and direction == 'down':
                        intermediate_x = x_coordinate - difference
                    intermediate_y = prices[i]

                    line_x.extend([x_coordinate, intermediate_x])
                    line_y.extend([previousY, intermediate_y])

                line_x.extend([intermediate_x, intermediate_x])
                line_y.extend([intermediate_y, prices[i]])
                marker_x.append(0)
                marker_y.append(midpoint)
                x_coordinate = intermediate_x
                prev_direction = direction
                previousY = prices[i]

    # 用少量 trace 畫出整條路徑
    if line_x:
        graph.add_trace(go.Scatter(
            x=line_x,
            y=line_y,
            mode='lines',
            line=dict(color='black', width=1.5),
            name='path',
            showlegend=False
        ))

    if marker_x:
        graph.add_trace(go.Scatter(
            x=marker_x,
            y=marker_y,
            mode='markers',
            marker=dict(symbol='circle', color='black', size=3),
            name='points',
            showlegend=False
        ))

    # 最後紅星
    graph.add_trace(go.Scatter(
        x=[x_coordinate],
        y=[previousY],
        mode='markers',
        marker=dict(symbol='star', color='red', size=10),
        name='latest',
        showlegend=False
    ))

    # 對角線
    graph.add_trace(go.Scatter(
        x=[-domain, domain],
        y=[midpoint - domain, midpoint + domain],
        mode='lines',
        line=dict(color='black', width=1),
        showlegend=False
    ))
