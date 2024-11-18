from rdflib import Graph
from pyshacl import validate

shacl_graph = Graph()
shacl_graph.parse("https://raw.githubusercontent.com/zazuko/cube-link/refs/heads/main/validation/profile-opendataswiss-lindas.ttl", format="turtle")

data_graph = Graph()
data_graph.parse("example/mock-cube.ttl", format="turtle")

conforms, results_graph, text = validate(data_graph, shacl_graph=shacl_graph, abort_on_first=True, inference="none", advanced=True)
print(text)

