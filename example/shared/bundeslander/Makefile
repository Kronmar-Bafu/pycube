.PHONY: all download ../../../py_cube/cube/shared_dimensions.py

all: data.pretty.geojson data.transformed.geojson data.ttl

data.geojson:
	echo "Original data downloaded from https://opendatalab.de/projects/geojson-utilities/"
	echo "    * Checked all checkboxes in Auswahlhilfe,"
	echo "    * then Optionen > \"Welche Flächen: Bundesland Flächen\","
	echo "    * then close Dialog, and click \"Export .geojson\" -> data.geojson"

data.pretty.geojson: data.geojson
	jq . $< > $@

data.transformed.geojson: transform.py data.pretty.geojson
	python transform.py data.geojson $@

data.ttl: data.transformed.geojson ../../../py_cube/cube/shared_dimensions.py
	cd ../../.. && \
	python cli.py shared convert_geojson example/shared/bundeslander/data.transformed.geojson example/shared/bundeslander/data.ttl  
