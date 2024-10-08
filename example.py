import pandas as pd
from math import pi
import py_cube
import yaml

import py_cube.lindas
from py_cube.lindas.upload import upload_ttl

mock_df = pd.read_csv("example/mock_data.csv")

with open("example/mock_cube.yml") as file:
    cube_yaml = yaml.safe_load(file)

cube = py_cube.Cube(dataframe=mock_df, cube_yaml=cube_yaml, environment="TEST", local=True)
cube.prepare_data()
cube.write_cube()
cube.write_observations()
cube.write_shape()
cube.serialize("example/mock-cube.ttl")
print(cube)

# upload_ttl(filename="./example/mock-cube.ttl", db_file="lindas.ini", environment="TEST")

