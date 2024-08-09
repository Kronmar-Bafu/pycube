import pandas as pd
import numpy as np
from math import pi

df = pd.DataFrame()
df["Jahr"] = np.repeat(np.arange(start=2000, stop=2023), 2)
df["Station"] = np.tile(["Bern", "Zürich"], 23)

x = np.arange(46)
value = np.sin(2*x) + np.sin(pi*x) - (0.5)**1.5*x + 23
print(value.max())
print(value.min())
df["Wert"] = value
error = (np.sin(3*x) + np.sin(pi/3*x) + 2)/4*10
df["Standardfehler"] = error

df.to_csv("tests/example_cube_data.csv", index=False)

print(df.head())