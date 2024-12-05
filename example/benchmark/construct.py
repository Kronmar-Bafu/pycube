import pandas as pd
import math
import numpy as np
from datetime import datetime, timedelta

def _construct_value1(row):
    return math.cos(float(row["index"]))

if __name__ == "__main__":
    for number_of_days in [7, 31, 182, 366, 731, 1827, 3653]:
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = start + timedelta(days=number_of_days)
        xx = np.arange(stop = number_of_days*24*6)
        benchmark_frame = pd.DataFrame({
            "date": pd.date_range(start=start, end=end, freq="10min"),
            "value1": math.cos(xx)*math.sin(xx)*np.exp(-xx/number_of_days),
            "value2": math.sin(xx)*math.cos(xx),

        })
        print(benchmark_frame.head())
