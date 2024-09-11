from SPARQLWrapper import SPARQLWrapper, JSON

def query_lindas(query: str, environment: str):
    # to do: hardcoded endpoint
    sparql = SPARQLWrapper("https://test.lindas.admin.ch/query")
    sparql.setQuery(query=query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["boolean"]