import json
import argparse
from urllib.parse import quote

def transform_geojson(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    transformed_features = []
    for feature in data['features']:
        name = feature['properties']['GEN']
        iri = f"https://example.org/land/{quote(feature['properties']['GEN'])}"
        transformed_feature = {
            'type': feature['type'],
            'geometry': feature['geometry'],
            'properties': {
                'iri': iri,
                'name_de': name
            }
        }
        transformed_features.append(transformed_feature)
    
    transformed_data = {
        'type': data['type'],
        '$schema': './schema.json',
        'features': transformed_features
    }
    
    with open(output_file, 'w') as f:
        json.dump(transformed_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Transform a GeoJSON file.')
    parser.add_argument('input_file', type=str, help='The input GeoJSON file')
    parser.add_argument('output_file', type=str, help='The output GeoJSON file')
    args = parser.parse_args()
    
    transform_geojson(args.input_file, args.output_file)

if __name__ == '__main__':
    main()