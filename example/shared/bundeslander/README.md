# German states shapes

```
cd examples/shared/bundeslander
make
curl 'http://localhost:3030/dataset' -H 'Content-Type: text/turtle' -X POST -T data.ttl
```
