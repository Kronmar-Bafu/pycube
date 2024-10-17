from SPARQLWrapper import SPARQLWrapper, JSON

def query_lindas(query: str, environment: str):
    # to do: hardcoded endpoint
    sparql = SPARQLWrapper("https://test.lindas.admin.ch/query")
    sparql.setQuery(query=query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["boolean"]


def cube_exists(cube_uri: str, environment: str):
    """
    This function checks whether a cube already exists in the provided environment using the Lindas query endpoint.
    If the cube already exists and the local flag is not set, the function will exit with an appropriate error message.
    Otherwise, the function will return the constructed cube URI as a URIRef object.

    Args:
        local (bool): A flag indicating whether the cube is local.
        environment (str): The environment of the cube.
    """
    query = f"ASK {{ <{cube_uri}> ?p ?o}}"
    return query_lindas(query, environment=environment)
        