import requests
import stardog
from configparser import ConfigParser



#URL = "https://stardog-test.cluster.ldbar.ch/lindas?graph=..."
#HEADERS = {'Content-Type': 'text/turtle', 'Authorization': }

# def uplod_ttl(filename: str, named_graph: str, password: str):
#     with open(filename) as file:
#         graph = file.read()
#         response = requests.request("POST", )


def _load_config(db_file:str, environment: str) -> dict:
    parser = ConfigParser()
    parser.read(db_file)
    
    config = {}
    if parser.has_section(environment):
        params = parser.items(environment)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f"Environment '{environment}' not found in db_file")

    return config

def upload_ttl(filename: str, db_file: str, environment: str):
    conn_details = _load_config(db_file, environment)
    print(conn_details)
    # with stardog.Connection("lindas", **conn_details) as conn:
    #     conn.begin()
    #     conn.add(stardog.content.File(file=filename))
    #     conn.commit()