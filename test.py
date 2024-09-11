import pandas as pd
from math import pi
import py_cube
import yaml

import py_cube.lindas
from py_cube.lindas.upload import upload_ttl

mock_df = pd.read_csv("example/mock_data.csv")

with open("example/mock_dimensions.yml") as file:
    shape_yaml = yaml.safe_load(file)

with open("example/mock_cube.yml") as file:
    cube_yaml = yaml.safe_load(file)

cube = py_cube.Cube(dataframe=mock_df, shape_yaml=shape_yaml, cube_yaml=cube_yaml, environment="TEST")

# upload_ttl("lindas.ini", "lindas.ini", "TEST")