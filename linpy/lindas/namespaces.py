from rdflib import Graph, Namespace


CUBE = Namespace("https://cube.link/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
LDADMIN = Namespace("https.//ld.admin.ch/application/")
META = Namespace("https://cube.link/meta/")
QUDT = Namespace("http://qudt.org/schema/qudt/")
RELATION = Namespace("https://cube.link/relation/")
SCHEMA = Namespace("http://schema.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")
TIME = Namespace("http://www.w3.org/2006/time#")
UNIT = Namespace("http://qudt.org/vocab/unit/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
VOID = Namespace("http://rdfs.org/ns/void#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")


Namespaces = {
    "cube": CUBE,
    "dcat": DCAT,
    "dct": DCT,
    "schema": SCHEMA,
    "foaf": FOAF,
    "ldadmin": LDADMIN,
    "meta": META,
    "qudt": QUDT,
    "relation": RELATION,
    "time": TIME,
    "unit": UNIT,
    "vcard": VCARD,
    "void": VOID,
    "geo": GEO,
}
