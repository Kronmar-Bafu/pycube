BASE_URI="http://localhost:3030/dataset"

echo "Loading kita..."
curl $BASE_URI -H 'Content-Type: text/turtle' -X POST -T example/kita/cube.ttl

echo "Loading bundeslander..."
curl $BASE_URI -H 'Content-Type: text/turtle' -X POST -T example/shared/bundeslander/data.ttl

echo "Loading meta..."
curl $BASE_URI -H 'Content-Type: text/turtle' -X POST -T /tmp/meta.ttl  

echo "Loading wind..."
curl $BASE_URI -H 'Content-Type: text/turtle' -X POST -T example/wind.ttl

