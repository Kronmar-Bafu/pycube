from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef, XSD
import pandas as pd
import numbers
import yaml
from py_cube.lindas.namespaces import *



cube = Namespace("https://cube.link/")


class Cube:
    _base_uri: URIRef
    _cube_uri: URIRef
    _cube_dict: dict
    _graph: Graph
    _dataframe: pd.DataFrame
    _shape_dict: dict
    _shape_URI: URIRef

    
    def __init__(self, dataframe: pd.DataFrame, shape_yaml: dict, cube_yaml: dict):
        self._dataframe = dataframe
        self._setup_cube_dict(cube_yaml=cube_yaml)
        self._setup_shape_dicts(shape_yaml=shape_yaml)
        self._graph = self._setup_graph()
        self._construct_obs_uri()
        self._apply_mappings()
        self._write_cube()
        self._write_obs()
        self._write_shape()
        self._graph.serialize("tests/mock-cube.ttl", format="turtle")

    def _setup_cube_dict(self, cube_yaml: dict):
        self._base_uri = URIRef(cube_yaml.get("Base-URI"))
        self._cube_dict = cube_yaml
        self._cube_uri = URIRef(self._base_uri + "/".join(["cube", str(cube_yaml.get("Identifier")), str(cube_yaml.get("Version"))]))
    
    def _setup_shape_dicts(self, shape_yaml: dict):
        self._shape_dict = shape_yaml.get("dimensions")
        self._shape_URI = URIRef(self._cube_uri + "/shape") 
        self._key_dimensions = [dim_name for dim_name, dim in self._shape_dict.items() if dim.get("dimension-type") == "Key Dimension"]

    def _setup_graph(self) -> Graph:
        graph = Graph()
        for prefix, nmspc in Namespaces.items():
            graph.bind(prefix=prefix, namespace=nmspc)
        try:
            graph.bind(prefix=self._cube_dict.get("Namespace"), namespace=Namespace(self._base_uri))
        except KeyError:
            print("no Namespace")
            pass
        return graph

    def _construct_obs_uri(self) -> None:
        self._dataframe['obs-uri'] = self._dataframe.apply(
            lambda row: self._cube_uri + "/observation/" + "_".join([str(row[key_dim]) for key_dim in self._key_dimensions]), axis=1
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

    def _write_cube(self):
        self._graph.add((self._cube_uri, RDF.type, CUBE.Cube))
        self._graph.add((self._cube_uri, RDF.type, SCHEMA.Dataset))
        self._graph.add((self._cube_uri, RDF.type, DCAT.Dataset))
        self._graph.add((self._cube_uri, RDF.type, VOID.Dataset))

        if self._cube_dict.get("Accrual Periodicity"):
            self._add_accrual_periodicity(self._cube_dict.get("Accrual Periodicity"))

    def _add_accrual_periodicity(self, periodicity: str):
        base_uri = URIRef("http://publications.europe.eu/resource/authority/frequency/")
        match periodicity:
            case "yearly": 
                self._graph.add((self._cube_uri, DCT.accrualPeriodicity, base_uri + "ANNUAL"))


    def _write_obs(self):
        self._dataframe.apply(self._add_observation, axis=1)

    def _add_observation(self, obs: pd.DataFrame):
        self._graph.add((self._cube_uri + "/ObservationSet", cube.observation, obs.name))

        for column in obs.keys():
            path = URIRef(self._base_uri + self._shape_dict.get(column).get("path"))
            sanitized_value = self._sanitize_value(obs.get(column))
            self._graph.add((obs.name, URIRef(path), sanitized_value))

    def _write_shape(self):
        for dim, dim_dict in self._shape_dict.items():
            shape = self._write_dimension_shape(dim_dict, self._dataframe[dim])
            self._graph.add((self._shape_URI, SH.property, shape))
    
    def _write_dimension_shape(self, dim_dict: dict, obs: pd.Series) -> BNode:
        dim_node = BNode()
        
        self._graph.add((dim_node, SH.minCount, Literal(1)))
        self._graph.add((dim_node, SH.maxCount, Literal(1)))

        for lan, name in dim_dict.get("name").items():
            self._graph.add((dim_node, SCHEMA.name, Literal(name, lang=lan)))
        for lan, desc in dim_dict.get("description").items():
            self._graph.add((dim_node, SCHEMA.description, Literal(desc, lang=lan)))
        
        self._graph.add((dim_node, SH.path, URIRef(self._base_uri + dim_dict.get("path"))))

        match dim_dict.get("dimension-type"):
            case "Key Dimension":
                self._graph.add((dim_node, RDF.type, CUBE.KeyDimension))
                # to do: alle KeyDimensions IRI? Angenommen für den Moment ja
                self._graph.add((dim_node, SH.nodeKind, SH.IRI))
                
            case "Measure Dimension":
                self._graph.add((dim_node, RDF.type, CUBE.MeasureDimension))
            case _ as unrecognized:
                print(f"Dimension Type '{unrecognized}' is not recognized")
        
        match dim_dict.get("scale-type"):
            case "nominal":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.NominalSclae))
            case "ordinal":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.OrdinalScale))
            case "interval":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.IntervalScale))
            case "ratio":
                self._graph.add((dim_node, QUDT.scaleType, QUDT.RatioScale))
            case _ as unrecognized:
                print(f"Scale Type '{unrecognized}' is not recognized")
        
        #try:
        #    match dim_dict.get("")

        return dim_node

    @staticmethod
    def _sanitize_value(value):
        if isinstance(value, numbers.Number):
            if pd.isna(value):
                return Literal("", datatype=cube.Undefined)
            else:
                return Literal(value, datatype=XSD.decimal)
        elif isinstance(value, URIRef):
            return value



