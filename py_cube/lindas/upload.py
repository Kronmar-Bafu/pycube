import requests

URL = "https:"

def uplod_ttl(filename: str, named_graph: str, password: str):
    with open(filename) as file:
        graph = file.read()
        response = requests.request("POST", )
