import numpy as np

def calculate_candlestick_range(data):
    ranges = []

    for i in range(1, len(data), 4):
        high = data[i]
        low = data[i + 1]
        if high >= low:
            range_value = high - low
        else:
            range_value = low - high
        ranges.append(range_value)

    if not ranges:
        return 0, 0, 0, 0, 0

    max_range = np.max(ranges)
    mean_range = np.mean(ranges)
    std_range = np.std(ranges)
    q3, q1 = np.percentile(ranges, [75, 25])
    iqr = q3 - q1

    std_range_rounded = round(std_range, 3)
    iqr_rounded = round(iqr, 3)
    data_range = np.max(data) - np.min(data)

    return max_range, data_range, mean_range, std_range_rounded, iqr_rounded