import pandas as pd
from math import pi
import py_cube
import yaml

import py_cube.lindas
from py_cube.lindas.upload import upload_ttl
from py_cube.lindas.query import cube_exists

mock_df = pd.read_csv("example/mock/data.csv")

with open("example/mock/description.yml") as file:
    cube_yaml = yaml.safe_load(file)

cube = py_cube.Cube(dataframe=mock_df, cube_yaml=cube_yaml, environment="TEST", local=True)
cube.prepare_data()
cube.write_cube()
cube.write_observations()
cube.write_shape()
cube.serialize("example/mock/cube.ttl")
print(cube)

if not cube_exists(cube_uri=cube.get_iri(), environment="TEST"):
    upload_ttl(filename="./example/mock-cube.ttl", db_file="lindas.ini", environment="TEST")

# upload_ttl(filename="./example/mock-cube.ttl", db_file="lindas.ini", environment="TEST")

modk_df_two_sided = pd.read_csv("py_cube/tests/test_data.csv")
with open("py_cube/tests/test.yml") as file:
    two_sided_yaml = yaml.safe_load(file)
cube_two_sided = py_cube.Cube(dataframe=modk_df_two_sided, cube_yaml=two_sided_yaml, environment="TEST", local=True)
cube_two_sided.prepare_data()
cube_two_sided.write_cube()
cube_two_sided.write_observations()
cube_two_sided.write_shape()

cube_two_sided.serialize("./example/mock-cube-two-sided.ttl")
upload_ttl(filename="./example/mock-cube-two-sided.ttl", db_file="lindas.ini", environment="TEST")