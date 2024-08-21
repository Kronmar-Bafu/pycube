import pandas as pd
import numpy as np
from math import pi
import cubelink
import yaml

mock_df = pd.read_csv("tests/mock_data.csv")

with open("tests/mock_dimensions.yml") as file:
    shape_yaml = yaml.safe_load(file)

with open("tests/mock_cube.yml") as file:
    cube_yaml = yaml.safe_load(file)

cube = cubelink.Cube(dataframe=mock_df, shape_yaml=shape_yaml, cube_yaml=cube_yaml)
