dev:
	uv run services/trades/src/trades/main.py
build:
	docker build -t trades:dev -f docker/trades.Dockerfile .
push:
	kind load docker-image trades:dev --name rwml-34fa
deploy: build	push
	kubectl delete -f deployment/dev/trades/trades.yaml
	kubectl apply -f deployment/dev/trades/trades.yaml
