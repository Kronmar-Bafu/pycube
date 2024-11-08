from py_cube import Cube
import pandas as pd
import pytest
import yaml

class TestClass:

    def setup_method(self):
        with open("py_cube/tests/test.yml") as file:
            cube_yaml = yaml.safe_load(file)
        test_df = pd.read_csv("py_cube/tests/test_data.csv")
        self.cube = Cube(
            dataframe=test_df, cube_yaml=cube_yaml,
            environment="TEST", local=True
        )

    def test_upper_uncertainty(self):
        sparql = (
            "prefix cube: <https://cube.link/>"
            "prefix dcterms: <http://purl.org/dc/terms/>"
            "prefix meta: <https://cube.link/meta/> "
            "prefix mock: <https://mock.ld.admin.ch/>"
            "prefix qudt: <http://qudt.org/schema/qudt/>"
            "prefix relation: <https://cube.link/relation/>"
            "prefix schema: <http://schema.org/>"
            "prefix sh: <http://www.w3.org/ns/shacl#>"
            "prefix unit: <http://qudt.org/vocab/unit/>"
            ""
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop schema:name \'Upper Unsicherheit\'@de ;"
            "    schema:description \'Upper Unsicherheit\'@de ;"
            "    sh:path mock:upperUncertainty ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    qudt:hasUnit unit:PERCENT ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceUpperBound ;"
            "      dcterms:type \"Confidence interval\" ;"
            "      meta:relatesTo mock:value2 ;"
            "    ] ."
            "}"
        )

        result = self.cube._graph.query(sparql)
        assert bool(result)

    def test_lower_uncertainty(self):
        sparql = (
            "prefix cube: <https://cube.link/>"
            "prefix dcterms: <http://purl.org/dc/terms/>"
            "prefix meta: <https://cube.link/meta/> "
            "prefix mock: <https://mock.ld.admin.ch/>"
            "prefix qudt: <http://qudt.org/schema/qudt/>"
            "prefix relation: <https://cube.link/relation/>"
            "prefix schema: <http://schema.org/>"
            "prefix sh: <http://www.w3.org/ns/shacl#>"
            "prefix unit: <http://qudt.org/vocab/unit/>"
            ""
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop schema:name \'Lower Unsicherheit\'@de ;"
            "    schema:description \'Lower Unsicherheit\'@de ;"
            "    sh:path mock:lowerUncertainty ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    qudt:hasUnit unit:PERCENT ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceLowerBound ;"
            "      dcterms:type \"Confidence interval\" ;"
            "      meta:relatesTo mock:value2 ;"
            "    ] ."
            "}"
        )

        result = self.cube._graph.query(sparql)
        assert bool(result)


