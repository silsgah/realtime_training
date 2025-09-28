################################################################################
## Development
################################################################################

# Runs the trades service as a standalone Pyton app (not Dockerized)
dev:
	uv run services/${service}/src/${service}/main.py

# Builds a docker image from a given Dockerfile
build-for-dev:
	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

# Push the docker image to the docker registry of our kind cluster
push-for-dev:
	# Exercise: do not push to the kind local registry, but the one on your Github account
	kind load docker-image ${service}:dev --name rwml-34fa

# Deploys the docker image to the kind cluster
deploy-for-dev: build-for-dev push-for-dev
	kubectl delete -f deployment/dev/${service}/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployment/dev/${service}/${service}.yaml

################################################################################
## Production
################################################################################

build-and-push:
	./scripts/build-and-push.sh ${image} ${env}
# Deploys a service to the given environment
deploy:
	./scripts/deploy.sh ${service} ${env}
	
build-and-push-for-prod:
	@BUILD_DATE=$$(date +%s); \
	echo "Build date: $$BUILD_DATE"; \
	docker buildx build --push --platform linux/amd64 \
		-t ghcr.io/silsgah/${service}:dev.0.1.5-beta.$$BUILD_DATE \
		-f docker/${service}.Dockerfile .


deploy-for-prod:
	kubectl delete -f deployment/prod/${service}/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployment/prod/${service}/${service}.yaml

lint:
	ruff check . --fix