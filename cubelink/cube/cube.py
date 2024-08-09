from rdflib import Graph, Literal, Namespace, URIRef, XSD
import pandas as pd
import numbers
import yaml



CUBE = Namespace("https://cube.link/")


class Cube:
    _base_uri: URIRef
    _cube_uri: URIRef
    _graph: Graph
    _dataframe: pd.DataFrame

    
    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe = dataframe

    def _add_observation(self, obs: pd.DataFrame):
        obs_uri = URIRef(self._base_uri + obs.name)

        self._graph.add((self._cube_uri + "ObservationSet", CUBE.observation, obs_uri))

        for column in obs.keys():
            sanitized_value = self._sanitize_value(obs.get(column))
            self._graph.add((obs_uri, URIRef(column), sanitized_value))

    @staticmethod
    def _sanitize_value(value):
        if isinstance(value, numbers.Number):
            if pd.isna(value):
                return Literal("", datatype=CUBE.Undefined)
            else:
                return Literal(value, datatype=XSD.decimal)
        elif isinstance(value, URIRef):
            return value



