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
    _shape_dict: dict

    
    def __init__(self, dataframe: pd.DataFrame, shape_yaml: dict, cube_yaml: dict):
        self._dataframe = dataframe
        self._setup_cube_dict(cube_yaml=cube_yaml)
        self._setup_shape_dicts(shape_yaml=shape_yaml)
        self._setup_graph()
        self._construct_obs_uri()
        self._apply_mappings()
        self._write_obs()
        self._graph.serialize("tests/mock-cube.ttl", format="turtle")
        print(self._dataframe.head())

    def _setup_cube_dict(self, cube_yaml: dict):
        self._base_uri = URIRef(cube_yaml.get("Base-URI"))
        self._cube_dict = cube_yaml
        self._cube_uri = URIRef("/".join([self._base_uri, "cube", str(cube_yaml.get("Identifier")), str(cube_yaml.get("Version"))]))
    
    def _setup_shape_dicts(self, shape_yaml: dict):
        self._shape_dict = shape_yaml.get("dimensions")
        self._key_dimensions = [dim_name for dim_name, dim in self._shape_dict.items() if dim.get("dimension-type") == "Key Dimension"]

    def _setup_graph(self):
        self._graph = Graph()

    def _construct_obs_uri(self) -> None:
        self._dataframe['obs-uri'] = self._dataframe.apply(
            lambda row: self._cube_uri + "/observation/" + "/".join([str(row[key_dim]) for key_dim in self._key_dimensions]), axis=1
        )
        self._dataframe['obs-uri'] = self._dataframe['obs-uri'].map(URIRef)
        self._dataframe = self._dataframe.set_index("obs-uri")

    def _apply_mappings(self) -> None:
        for dim_name, dim_dict in self._shape_dict.items():
            if "mapping" in dim_dict:
                mapping = dim_dict.get("mapping")
                match mapping.get("type"):
                    case "additive":
                        base = mapping.get("base") + "{}"
                        self._dataframe[dim_name] = self._dataframe[dim_name].map(base.format)
                    case "replace":
                        self._dataframe[dim_name] = self._dataframe[dim_name].map(mapping.get("replacements"))
                self._dataframe[dim_name] = self._dataframe[dim_name].map(URIRef)

    def _write_obs(self):
        self._dataframe.apply(self._add_observation, axis=1)

    def _add_observation(self, obs: pd.DataFrame):
        print(obs.name)
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



