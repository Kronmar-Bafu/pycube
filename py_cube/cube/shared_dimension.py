from rdflib import Graph, Literal, RDF, URIRef
from py_cube.lindas.namespaces import *
from shapely.geometry import shape
import json
import argparse


class GeoSharedDimension(object):
    _base_uri: URIRef
    _graph: Graph
    _description: dict

    def __init__(self, base_uri: URIRef, description: dict, graph: Graph):
        self._base_uri = base_uri
        self._graph = graph
        self._description = description
    
    def _setup_graph(self) -> Graph:
        """Set up the graph by binding namespaces and returning the graph object.
        
        Returns:
            Graph: The graph object with namespaces bound.
        """
        graph = Graph()
        for prefix, nmspc in Namespaces.items():
            graph.bind(prefix=prefix, namespace=nmspc)
        try:
            graph.bind(prefix=self._cube_dict.get("Namespace"), namespace=Namespace(self._base_uri))
        except KeyError:
            print("no Namespace")
            pass
        return graph


    def _geojson_to_wkt(self, geojson: dict) -> str:
        """Convert GeoJSON to WKT.
        
        Returns:
            str: The WKT string.
        """
        if not geojson:
            return None
        geom = shape(geojson)
        return geom.wkt


    def _add_geo_feature_to_graph(self, geojson_feature):
        properties = geojson_feature.get("properties")
        if not properties:
            raise ValueError("Feature must have properties")
        iri = properties.get("iri")
        if not iri:
            raise ValueError("Feature must have an IRI")
        feature = URIRef(iri)
        self._graph.add((feature, RDF.type, URIRef("http://schema.org/Place")))

        for lang in ["fr", "en", "de", "it"]:
            name_key = f"name_{lang}"
            if name_key in properties:
                self._graph.add((feature, URIRef("http://schema.org/name"), Literal(properties[name_key], lang=lang)))

        geometry = URIRef(f"{iri}/geometry")
        self._graph.add((feature, URIRef("http://www.opengis.net/ont/geosparql#hasGeometry"), geometry))
        wkt = self._geojson_to_wkt(geojson_feature['geometry'])
        if wkt:
            self._graph.add((geometry, URIRef("http://www.opengis.net/ont/geosparql#asWKT"), Literal(wkt, datatype=URIRef("http://www.opengis.net/ont/geosparql#wktLiteral"))))


    def serialize(self, filename: str) -> None:
        """Serialize the cube to a file.

        This function serializes the cube to the given file name in turtle format.

        Args:
            filename (str): The name of the file to write the cube to.

        Returns:
            None
        """
        self._graph.serialize(destination=filename, format="turtle", encoding="utf-8")


def convert_geojson_to_ttl(geojson_filename, ttl_filename):
    with open(geojson_filename, 'r') as f:
        geojson_data = json.load(f)

    base_uri = URIRef("http://example.org/base")
    description = {}
    graph = Graph()

    shared_dimension = GeoSharedDimension(base_uri, description, graph)

    for feature in geojson_data.get("features", []):
        print(f"Adding feature {feature['properties']['name_de']}")
        shared_dimension._add_geo_feature_to_graph(feature)

    shared_dimension.serialize(ttl_filename)
