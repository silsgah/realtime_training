## Goals for today

- [x] Deploy Kafka in our dev kubernetes cluster.
- [x] Deploy the Kafka UI in our dev kubernetes cluster.

## create namespace for kafka in kub
1. kubectl create namespace kafka


1. kubectl -n kafka port-forward svc/kafka-ui 8182:8080
3. uv run services/trades/src/trades/main.py

2. uv add quixstreams