import json
import requests
import os

examples_dir = "example"


def load_example(example_id, base_uri="http://localhost:3030/dataset"):
    file_path = os.path.join(examples_dir, example_id, 'cube.ttl')
    with open(file_path, 'rb') as f:
        response = requests.post(base_uri, headers={"Content-Type": "text/turtle"}, data=f)
        response.raise_for_status()


def list_examples(language="en"):
    result = []
    for root, dirs, files in os.walk(examples_dir):
        if "cube.ttl" in files and "description.json" in files:
            description_path = os.path.join(root, "description.json")
            with open(description_path, 'r') as desc_file:
                desc = json.load(desc_file)
                name = desc.get("Name", {}).get(language, "")
                description = desc.get("Description", {}).get(language, "")
            result.append({
                "id": os.path.relpath(root, examples_dir),
                "name": name,
                "description": description
            })
    return result
