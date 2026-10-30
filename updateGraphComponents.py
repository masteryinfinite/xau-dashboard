symbol_ranges = {
    'XAUUSD': (1, 50, 1, 200),
    'EURUSD': (50, 150, 200, 800),
    'GBPUSD': (200, 500, 500, 1500),
    'USDJPY': (300, 500, 3500, 5000),
    'UK100': (10, 100, 100, 300),
    'HK50': (50, 200, 500, 1200),
    'AUDUSD': (50, 200, 400, 800),
    'NZDUSD': (100, 300, 300, 1000),
}

def updateComponents(symbol):
    domain_min_value = symbol_ranges[symbol][2]
    domain_max_value = symbol_ranges[symbol][3]
    domain_step = (domain_max_value - domain_min_value) / 10
    domain_marks = {i: str(i) for i in range(domain_min_value, domain_max_value + 1, int(domain_step))}

    threshold_min_value = symbol_ranges[symbol][0]
    threshold_max_value = symbol_ranges[symbol][1]
    threshold_step = (threshold_max_value - threshold_min_value) / 10
    threshold_marks = {i: str(i) for i in range(threshold_min_value, threshold_max_value + 1, int(threshold_step))}

    return threshold_min_value, threshold_max_value, domain_min_value, domain_max_value, domain_marks, threshold_marks