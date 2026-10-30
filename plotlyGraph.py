import plotly.graph_objs as go

def plotly_stock_prices(min, max, prices, domain, graph, threshold):
    
    midpoint = (min + max) / 2
    prev_direction = ''
    onslopeFlag = False
    previousY = 0
    
    interval = int((max - min) / 10)
    if interval == 0:
        interval = 1

    for i in range(20):
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint - domain + interval * (i + 1),
            x1=domain, y1=midpoint + domain + interval * (i + 1),
            line=dict(color="rgba(214, 219, 223, 0.5)", width=2, dash="solid"),
        )
    for i in range(20):
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint - domain - interval * (i + 1),
            x1=domain, y1=midpoint + domain - interval * (i + 1),
            line=dict(color="rgba(214, 219, 223, 0.5)", width=2, dash="solid"),
        )
    for i in range(20):
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint + domain - interval * (i),
            x1=domain, y1=midpoint - domain - interval * (i),
            line=dict(color="rgba(214, 219, 223, 0.5)", width=2, dash="solid"),
        )
    for i in range(20):
        graph.add_shape(
            type="line",
            x0=-domain, y0=midpoint + domain + interval * (i + 1),
            x1=domain, y1=midpoint - domain + interval * (i + 1),
            line=dict(color="rgba(214, 219, 223, 0.5)", width=2, dash="solid"),
        )

    for i in range(len(prices)):
        if i > 0:
            difference = prices[i] - previousY
            current_y = (previousY + midpoint + x_coordinate) / 2
            direction = 'up' if difference > 0 else 'down'

            if direction == prev_direction or i == 1 or prev_direction == '':
                if (prices[i] > current_y and direction == 'down') or (prices[i] < current_y and direction == 'up'):
                    intermediate_x = x_coordinate - difference
                    if (prices[i] < current_y and direction == 'up'): intermediate_x = x_coordinate - difference
                    if (prices[i] < current_y and direction == 'down'): intermediate_x = x_coordinate
                    if (prices[i] > current_y and direction == 'up'): intermediate_x = x_coordinate
                    if (prices[i] > current_y and direction == 'down'): intermediate_x = x_coordinate - difference
                    intermediate_y = prices[i]

                    graph.add_trace(go.Scatter(
                        x=[x_coordinate, intermediate_x],
                        y=[previousY, intermediate_y],
                        mode='lines',
                        name=str(i) + ':' + str(intermediate_y),
                        line=dict(color='black')
                    ))
                    previousY = intermediate_y
                    x_coordinate = intermediate_x
                else:
                    if (previousY < current_y and direction == 'down') or (previousY > current_y and direction == 'up'):
                        intermediate_x = x_coordinate
                    else:
                        if (prices[i] > current_y and previousY < current_y) or (prices[i] < current_y and previousY > current_y):
                            if (x_coordinate == 0):
                                intermediate_y = (midpoint + previousY) / 2
                                intermediate_x = intermediate_y - midpoint
                            elif (x_coordinate != 0):
                                referenceC = previousY + x_coordinate
                                intermediate_y = (referenceC + midpoint) / 2
                                intermediate_x = intermediate_y - midpoint

                            graph.add_trace(go.Scatter(
                                x=[x_coordinate, intermediate_x],
                                y=[previousY, intermediate_y],
                                mode='lines',
                                name=str(i) + ':' + str(intermediate_y),
                                line=dict(color='black')
                            ))
                            if intermediate_y != min:
                                graph.add_trace(go.Scatter(
                                    x=[intermediate_x],
                                    y=[prices[i]],
                                    mode='markers',
                                    name=str(i) + ':' + str(prices[i]),
                                    marker=dict(symbol='circle', color='black', size=2)
                                ))
                                x_coordinate = intermediate_x
                        else:
                            if (prices[i] <= current_y and direction == 'up'): intermediate_x = x_coordinate - difference
                            if (prices[i] <= current_y and direction == 'down'): intermediate_x = x_coordinate
                            if (prices[i] >= current_y and direction == 'up'): intermediate_x = x_coordinate
                            if (prices[i] >= current_y and direction == 'down'): intermediate_x = x_coordinate - difference
                            intermediate_y = prices[i]

                            graph.add_trace(go.Scatter(
                                x=[x_coordinate, intermediate_x],
                                y=[previousY, intermediate_y],
                                mode='lines',
                                name=str(i) + ':' + str(intermediate_y),
                                line=dict(color='black')
                            ))

                        graph.add_trace(go.Scatter(
                            x=[intermediate_x, intermediate_x],
                            y=[intermediate_y, prices[i]],
                            mode='lines',
                            name=str(i) + ':' + str(prices[i]),
                            line=dict(color='black')
                        ))
                        graph.add_trace(go.Scatter(
                            x=[0],
                            y=[midpoint],
                            mode='markers',
                            name=str(i) + ':' + str(midpoint),
                            marker=dict(symbol='circle', color='black', size=2)
                        ))
                        x_coordinate = intermediate_x
                        prev_direction = direction

                    graph.add_trace(go.Scatter(
                        x=[intermediate_x],
                        y=[prices[i]],
                        mode='markers',
                        name=str(i) + ':' + str(prices[i]),
                        marker=dict(symbol='circle', color='black', size=2)
                    ))

                    graph.add_trace(go.Scatter(
                        x=[x_coordinate, intermediate_x],
                        y=[intermediate_y, prices[i]],
                        mode='lines',
                        name=str(i) + ':' + str(prices[i]),
                        line=dict(color='black')
                    ))
                    prev_direction = direction
                    x_coordinate = intermediate_x
                    previousY = prices[i]
            else:
                onslopeFlag = True
                if abs(difference) >= threshold:
                    if (prices[i] > current_y and previousY < current_y) or (previousY < current_y and previousY > current_y) or (prices[i] < current_y and previousY > current_y):
                        if (x_coordinate == 0):
                            intermediate_y = (midpoint + previousY) / 2
                            intermediate_x = intermediate_y - midpoint
                        elif (x_coordinate != 0):
                            referenceC = previousY + x_coordinate
                            intermediate_y = (referenceC + midpoint) / 2
                            intermediate_x = intermediate_y - midpoint

                        graph.add_trace(go.Scatter(
                            x=[x_coordinate, intermediate_x],
                            y=[previousY, intermediate_y],
                            mode='lines',
                            name=str(i) + ':' + str(intermediate_y),
                            line=dict(color='black')
                        ))
                        if intermediate_y != min:
                            graph.add_trace(go.Scatter(
                                x=[intermediate_x],
                                y=[prices[i]],
                                mode='markers',
                                name=str(i) + ':' + str(prices[i]),
                                marker=dict(symbol='circle', color='black', size=2)
                            ))
                    else:
                        if (prices[i] < current_y and direction == 'up'): intermediate_x = x_coordinate - difference
                        if (prices[i] < current_y and direction == 'down'): intermediate_x = x_coordinate
                        if (prices[i] > current_y and direction == 'up'): intermediate_x = x_coordinate
                        if (prices[i] > current_y and direction == 'down'): intermediate_x = x_coordinate - difference
                        intermediate_y = prices[i]

                        graph.add_trace(go.Scatter(
                            x=[x_coordinate, intermediate_x],
                            y=[previousY, intermediate_y],
                            mode='lines',
                            name=str(i) + ':' + str(intermediate_y),
                            line=dict(color='black')
                        ))
                    graph.add_trace(go.Scatter(
                        x=[intermediate_x, intermediate_x],
                        y=[intermediate_y, prices[i]],
                        mode='lines',
                        name=str(i) + ':' + str(prices[i]),
                        line=dict(color='black')
                    ))
                    graph.add_trace(go.Scatter(
                        x=[0],
                        y=[midpoint],
                        mode='markers',
                        name=str(i) + ':' + str(midpoint),
                        marker=dict(symbol='circle', color='black', size=2)
                    ))
                    x_coordinate = intermediate_x
                    prev_direction = direction
                    previousY = prices[i]
        else:
            graph.add_trace(go.Scatter(
                x=[0],
                y=[midpoint],
                mode='markers',
                name=str(i) + ':' + str(midpoint),
                marker=dict(symbol='star', color='black', size=10)
            ))
            x_coordinate = 0
            previousY = prices[i]

    graph.add_trace(go.Scatter(
        x=[x_coordinate],
        y=[previousY],
        mode='markers',
        name=str(prices[-1] if prices else 0),
        marker=dict(symbol='star', color='red', size=8),
    ))
    graph.add_trace(go.Scatter(
        x=[-domain, domain],
        y=[midpoint - domain, midpoint + domain],
        mode='lines',
        line=dict(color='black')
    ))