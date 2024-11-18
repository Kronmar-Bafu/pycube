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
        self.cube.prepare_data()
        self.cube.write_cube()
        self.cube.write_observations()
        self.cube.write_shape()

    def test_upper_uncertainty(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path mock:upperUncertainty ;"
            "    schema1:name 'Upper Unsicherheit'@de ;"
            "    sh:maxCount 1 ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceUpperBound ;"
            '      dct:type "Confidence interval" ;'
            "      meta:relatesTo mock:value ;"
            "    ] ."
            "}"
        )

        result = self.cube._graph.query(sparql)
        assert bool(result)

    def test_lower_uncertainty(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop schema1:name 'Lower Unsicherheit'@de ;"
            "    schema1:description 'Lower Unsicherheit'@de ;"
            "    sh:path mock:lowerUncertainty ;"
            "    qudt:scaleType qudt:RatioScale ;"
            "    qudt:hasUnit unit:PERCENT ;"
            "    meta:dimensionRelation ["
            "      a relation:ConfidenceLowerBound ;"
            "      dct:type 'Confidence interval' ;"
            "      meta:relatesTo mock:value ;"
            "    ] ."
            "}"
        )

        result = self.cube._graph.query(sparql)
        assert bool(result)

    def test_standard_error(self):
        pass

    def test_point_limit(self):
        sparql = (
            "ASK"
            "{"
            "  ?shape a cube:Constraint ;"
            "    sh:property ?prop ."
            "  ?prop sh:path mock:value2 ;"
            "    meta:annotation ?annotation ."
            "  ?annotation a meta:Limit ;"
            "    schema:value 11 ;"
            "    schema1:name 'Richtwert 2020 in Zürich'@de ;"
            "    meta:annotationContext ["
            "      sh:path mock:year ;"
            "      sh:hasValue <https://ld.admin.ch/time/year/2000> ;"
            "    ] , ["
            "      sh:path mock:station ;"
            "      sh:hasValue <https://mock.ld.admin.ch/station/01> ;"
            "    ] ."
            "}"
        )

        result = self.cube._graph.query(sparql)
        assert bool(result)

