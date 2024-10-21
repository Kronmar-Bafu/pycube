all: cube.ttl

data.csv:
	echo "1. Download CSV from https://data.europa.eu/data/datasets/https-www-datenportal-bmbf-de-portal-2-2-5?locale=en"
	# Add your download command here
	echo "2. Clean the file (removing merged cells, removing rows about the header, removing extra Anzahl grouping columns)"
	echo "3. Export as CSV"

cube.ttl: data.csv description.json
	echo "Navigating to the project root directory"
	cd ../.. && \
		python cli.py serialize example/kita/ example/kita/cube.ttl
