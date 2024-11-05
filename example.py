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

modk_df_two_sided = pd.read_csv("py_cube/tests/test_data.csv")
with open("py_cube/tests/test.yml") as file:
    two_sided_yaml = yaml.safe_load(file)
cube_two_sided = py_cube.Cube(dataframe=modk_df_two_sided, cube_yaml=two_sided_yaml, environment="TEST", local=True)
cube.prepare_data()
cube.write_cube()
cube.write_observations()
cube.write_shape()

sparql = sparql = (
            "prefix cube: <https://cube.link/>"
            "prefix dcterms: <http://purl.org/dc/terms/>"
            "prefix meta: <https://cube.link/meta/> "
            "prefix mock: <https://mock.ld.admin.ch/>"
            "prefix qudt: <http://qudt.org/schema/qudt/>"
            "prefix relation: <https://cube.link/relation/>"
            "prefix schema: <http://schema.org/>"
            "prefix sh: <http.//w3.org/ns/shacl#>"
            "prefix unit: <http://qudt.org/vocab/unit/>"
            ""
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop schema:name \'Upper Unsicherheit\'@de ;"
            "    schema:description \'Upper Unsicherheit\'@de ;"
            "    sh:path mock:upperUncertainty ;"
            "    sh:scale sh:ratio ;"
            "    qudt:hasUnit unit:PERCENT ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceUpperBound ;"
            "      dcterms:type \"Confidence interval\" ;"
            "      meta:relatesTo mock:value2 ;"
            "    ] ."
            "}"
        )

result = cube_two_sided._graph.query(sparql)
print(result)