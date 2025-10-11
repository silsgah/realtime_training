## Goals for today

- [x] Deploy Kafka in our dev kubernetes cluster.
- [x] Deploy the Kafka UI in our dev kubernetes cluster.
kubectl config use-context kind-rwml-34fa
kubectl config current-context
kubectl config use-context arn:aws:eks:us-east-1:664442573483:cluster/prod
## create namespace for kafka in kub
1. Enable the script for installation chmod +x create_cluster.sh
2. Run the create_cluser.sh script -- does kubernestes-kafka, create namespace
3. Create the pyproject.toml file by running uv init trades --lib
4. Deploy kafka UI in kub
5. kubectl -n kafka port-forward svc/kafka-ui 8182:8080

1. kubectl -n kafka port-forward svc/kafka-ui 8182:8080
3. uv run services/trades/src/trades/main.py

2. uv add quixstreams

uv tool install pre-commit
uv tool install ruff   
Install ruff
install pre-cpmmit
configure pre-commit.yaml file
cat ~/.kube/config


Here's the updated documentation including commands to delete resources if needed:
Deleting Existing Resources (If Needed)
To clean up existing resources before redeployment:
bash# Delete Kafka UI
kubectl delete deployment kafka-ui -n kafka
kubectl delete service kafka-ui -n kafka

# Delete Kafka cluster
kubectl delete -f manifests/kafka-e11b.yaml -n kafka

# Delete Strimzi operator
kubectl delete -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Delete Kafka namespace (only if you want to start completely fresh)
kubectl delete namespace kafka
Kafka Deployment
export kind cluster to kube config
export KUBECONFIG="$(kind get kubeconfig --name localcluster)"
Create Kafka namespace:

bash kubectl create namespace kafka

Install Strimzi Kafka operator:

bash kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

Deploy Kafka cluster:
kubectl -n kafka port-forward svc/kafka-ui 8182:8080
bash
kubectl apply -f manifests/kafka-e11b.yaml -n kafka

kubectl apply -f deployment/dev/kind/kafka-ui-all-in-one.yaml
Kafka UI Deployment

Deploy Kafka UI with the resource configuration to match your cluster:
kubectl apply -f kafka-ui.yaml -n kafka

Patch Kafka UI to reduce memory requirements (if facing resource constraints):

bash kubectl patch deployment kafka-ui -n kafka -p '{"spec":{"template":{"spec":{"containers":[{"name":"kafka-ui","resources":{"requests":{"memory":"256Mi"},"limits":{"memory":"512Mi"}}}]}}}}'

Expose Kafka UI with a LoadBalancer:

bash kubectl patch svc kafka-ui -n kafka -p '{"spec":{"type":"LoadBalancer"}}'

Get the external access information:

kubectl get svc kafka-ui -n kafka

Apply the updated configuration:

bash kubectl apply -f trades-deployment.yaml -n kafka

Check if the deployment was successful:

bashkubectl get deployment trades -n kafka

Check the pod status:

bashkubectl get pods -n kafka -l app=trades

If you need to view logs:

bash kubectl logs -f deployment/trades -n kafka

kubectl set env deployment/trades KAFKA_BROKER_ADDRESS=kafka-e11b-kafka-bootstrap.kafka.svc.cluster.local:9092 -n kafka
ssh into pod
kubectl exec -it deployment/trades -n kafka -- sh        
You can also verify the nodePort assigned to your Kafka external service by running:
kubectl get svc -n kafka
Look for something like kafka-bootstrap or similar that exposes port 9094 over NodePort.
kubectl set env deployment/trades KAFKA_BROKER_ADDRESS=kafka-e11b-kafka-bootstrap.kafka.svc.cluster.local:9092 -n kafka
kubectl logs -f -l app=candles -n kafka 
kubectl port-forward svc/kafka-ui 8080:8080 -n kafka
Then open http://localhost:8080 in your browser.
b. Change the Service type to LoadBalancer if your cloud provider supports it:
bashkubectl patch svc kafka-ui -n kafka -p '{"spec":{"type":"LoadBalancer"}}'
Then check the external IP with:
bashkubectl get svc kafka-ui -n kafka
c. Set up an Ingress for it (more advanced, requires Ingress controller).

Once you've accessed the UI, you should see the Kafka UI interface where you can monitor and manage your Kafka cluster.
To understand why it's still pending, check the pod description again:
bashkubectl describe pod -n kafka -l app.kubernetes.io/name=kafka-ui
#monitoring the events on kubenertes
kubectl get events -A -w
logz.io

brew install ta-lib
uv add TA-Lib

kubectl config get-contexts
Show all available contexts:
bash
Copy
Edit
kubectl config get-contexts
Let’s say the name from the second row is my-other-cluster-context:

bash
Copy
Edit
kubectl config use-context my-other-cluster-context
If for example you want to use rwml-34fa:

bash
Copy
Edit
kubectl config use-context kind-rwml-34fa
Run this to write the kind cluster config to your kubeconfig file:

bash
Copy
Edit
kind export kubeconfig --name rwml-34fa
Do the same for cluster-123 if needed:

bash
Copy
Edit
kind export kubeconfig --name cluster-123

. Delete All Kind Clusters
bash
kind delete cluster --name rwml-34fa
kind delete cluster --name cluster-123
2. Verify No Running Clusters Remain
bash
kind get clusters  # Should return empty
docker ps -a | grep kind  # Check for any remaining containers
3. Clean Up Kubernetes Config
bash
# Remove all Kind-related contexts
kubectl config delete-context kind-rwml-34fa
kubectl config delete-context kind-cluster-123

# Verify remaining contexts
kubectl config get-contexts
4. Reset Docker (Optional)
If you want a completely fresh start:

bash
# Remove orphaned Kind containers/networks
docker system prune -f
docker network prune -f

# For complete reset (warning: affects all containers):
docker system prune -a -f --volumes
5. Verify Clean State
bash
# Check all components
kind get clusters
kubectl config get-contexts
docker ps -a | grep kind
6. Create New Cluster (When Ready)
bash
kind create cluster --name new-cluster
kubectl cluster-info

cat ~/.kube/config
kubectl config view --raw

Run this command to regenerate the kubeconfig for your existing kind cluster:

bash
Copy
Edit
kind export kubeconfig --name rwml-34fa
This will regenerate ~/.kube/config with context info for rwml-34fa.

✅ Then, confirm it worked:
bash
Copy
Edit
kubectl config get-contexts
kubectl config use-context kind-rwml-34fa
kubectl cluster-info

Next Step (Optional): Add DigitalOcean Cluster
If you want to re-add your DigitalOcean cluster, and you still have that prod.yaml file, you can do:

bash
Copy
Edit
kubectl config view --flatten --merge -o yaml > ~/.kube/temp_config.yaml
KUBECONFIG=~/.kube/temp_config.yaml:~/prod.yaml kubectl config view --flatten > ~/.kube/confi
kubectl port-forward svc/grafana -n monitoring 3000:80
kubectl apply --recursive -f manifests/mlflow-minio-secret.yaml


### mlflow

#### Create a secret for mlflow

in ```manifests/mlflow-minio-secret.yaml``` add:

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: mlflow-minio-secret
  namespace: mlflow
type: Opaque
stringData:
  AccessKeyID: REDACTED
  SecretKey: REDACTED
```
create mflow namespace
kubectl create namespace mlflow
Apply it ``` kubectl apply --recursive -f manifests/mlflow-minio-secret.yaml```

#### Helm install

```sh
helm upgrade --install --create-namespace --wait mlflow oci://registry-1.docker.io/bitnamicharts/mlflow --namespace=mlflow --values deployment/dev/kind/manifests/mlflow-values.yaml
```

In a shell in the risingwave-postgresql-0 pod

pass: ```postgres``

```sh
psql -U postgres -h risingwave-postgresql.risingwave.svc.cluster.local
```

```sql
CREATE USER mlflow WITH ENCRYPTED password 'mlflow';
CREATE DATABASE mlflow WITH ENCODING='UTF8' OWNER=mlflow;
CREATE DATABASE mlflow_auth WITH ENCODING='UTF8' OWNER=mlflow;
```

```sh
kubectl -n mlflow port-forward svc/mlflow-tracking 8889:80
```

user / passwords are autogenerated, you have to do a 1 liner:

```sh
kubectl get secrets -n mlflow mlflow-tracking -o json | jq -r '.data."admin-password"' | base64 -D
```

```sh
kubectl get secrets -n mlflow mlflow-tracking -o json | jq -r '.data."admin-user"' | base64 -D
```

or

```sh
kubectl get secret --namespace mlflow mlflow-tracking -o jsonpath="{.data.admin-password }"  | base64 -D
```

```sh
kubectl get secret --namespace mlflow mlflow-tracking -o jsonpath="{.data.admin-user }"  | base64 -D
```

Uninstall with:

```sh
helm uninstall mlflow -n mlflow
```
\q
\l
\dt
kubectl port-forward svc/mlflow-tracking 5000:80 -n mlflow
Silass-MacBook-Pro:~/documents/llm/realtime_044/deployment/dev/kind/manifests (feature-2) $ helm uninstall mlflow -n mlflow
release "mlflow" uninstalled
Silass-MacBook-Pro:~/documents/llm/realtime_044/deployment/dev/kind/manifests (feature-2) $ kubectl delete namespace mlflow
namespace "mlflow" deleted
Silass-MacBook-Pro:~/documents/llm/realtime_044/deployment/dev/kind/manifests (feature-2) $ kubectl delete secret mlflow-minio-secret -n mlflow
kubectl run → creates a temporary pod in Kubernetes.

-n mlflow → puts the pod in the mlflow namespace.

db-test → the name of the pod being created.

--rm → automatically deletes the pod when you exit the shell.

-it → allocates a TTY and keeps it interactive, so you can type commands inside the pod.

--image=postgres → the pod will run the official PostgreSQL image. This gives you psql and other PostgreSQL tools inside the pod.

--env="PGPASSWORD=mlflow" → sets the PGPASSWORD environment variable, so you don’t have to type the password when using psql.

-- bash → runs bash inside the container so you get a shell prompt.

Once inside the test2 run this
psql -h risingwave-postgresql.risingwave.svc.cluster.local -U mlflow -d mlflow

kubectl run -n mlflow db-test --rm -it --image=postgres --env="PGPASSWORD=mlflow" -- bash
<!-- 
//Make sure Python and boto3 are available (the Bitnami MLflow image should have them).
Run a Python shell: -->
kubectl exec -n mlflow -it mlflow-tracking-8bcd54cd6-qbvvq -- sh
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://risingwave-minio.risingwave.svc.cluster.local:9000',
    aws_access_key_id='JfU7XqGpNflQjpauJfvx',
    aws_secret_access_key='0LiiBx3dm7L9a15Ip63vkOEtVYKlDmTpsdjMaogO'
)

print(s3.list_buckets())

kubectl get secrets -n risingwave---get secrets in a namesapce
kubectl get secret risingwave-minio -n risingwave -o yaml -print them out

Test with:
kubectl get svc -A | grep risingwave
gives you all the services
kubectl port-forward svc/risingwave-postgresql 5432:5432 -n risingwave
kubectl port-forward svc/risingwave 4567:4567 -n risingwave

port forwarding
psql -h localhost -p 4567 -U root -d dev

password is postgres
psql -h localhost -p 4567 -U postgres -d dev ---- use this
psql -h localhost -p 4567 -U root -d dev
# Password: 123456 (as per your manifest)

kubectl get svc -A | grep risingwave

kubectl get svc -A | grep risingwave

$ kubectl port-forward svc/risingwave 4567:4567 -n risingwave
engine = create_engine("risingwave://postgres:postgres@localhost:4567/mlflow")

SELECT * FROM technical_indicators WHERE pair = 'BTC.EUR' LIMIT 10;


direnv allow

export MLFLOW_TRACKING_URI='http://localhost:8283'
export RISINGWAVE_HOST='localhost'
export RISINGWAVE_PORT=5000
export RISINGWAVE_USER='root'
export RISINGWAVE_PASSWORD='none'
export RISINGWAVE_DATABASE='dev'
export PAIR='BTC/USD'
export training_data_days=100
export candle_seconds=60
export prediction_horizon_seconds=300
export train_test_split_ratio=0.8
export n_rows_for_data_profiling=1
export eda_report_html_path='./eda_report.html'

make deploy image=backfill-technical-indicators env=dev

kubectl get pods -n kafka -l app.kubernetes.io/name=kafka-ui -w
kubectl get nodes -o wide
make dev service=trades
make dev service=candles
psql -h localhost -p 4567 -U postgres -d dev
make deploy image=backfill-technical-indicators env=dev
make build-and-push image=training-pipeline env=dev
make deploy service=training-pipeline env=dev
make build-and-push image=prediction-generator env=dev
make deploy service=prediction-generator env=dev
kubectl exec -it risingwave-postgresql-0 -n risingwave -- psql -U postgres   

| Component  | Role                           | Interaction                                                     |
| ---------- | ------------------------------ | --------------------------------------------------------------- |
| Kubernetes | Orchestrates containers        | Hosts MLflow, Postgres, MinIO pods                              |
| Pod        | Single or multi-container unit | MLflow pod runs MLflow server, init containers for DB/S3 checks |
| Service    | Stable network endpoint        | MLflow tracking service points to pod(s)                        |
| kubectl    | CLI                            | Manage pods, services, secrets, logs                            |
| Helm       | Package manager                | Deploys MLflow chart with DB/MinIO configuration                |

kubectl get secret -n mlflow mlflow-tracking -o jsonpath="{.data.admin-user}" | base64 -d
kubectl get secret -n mlflow mlflow-tracking -o jsonpath="{.data.admin-password}" | base64 -d

# 1. Sync workspace dependencies
uv sync --frozen

# 2. Build Docker image using root context and your docker/Dockerfile
docker build -t training-pipeline:dev -f docker/training-pipeline.Dockerfile .
# load it
kind load docker-image training-pipeline:dev --name rwml-34fa
# 3. Restart the training-pipeline deployment
kubectl rollout restart deployment training-pipeline -n rwml
# 4. If you changed Kubernetes manifests (e.g., environment variables, volume mounts, replicas):Use:
kustomize build training-pipeline | kubectl apply -f -

Delete Just the Pods (temporary stop)
kubectl delete pod trades-historical-5b9c7468d-7f8zh -n default
kubectl delete pod trades-historical-c5746c5c7-fwwth -n rwml
To see what controlling them  prediction-generator-6548b78645-mzc6l
kubectl get deployment,statefulset,job,cronjob -A | grep trades-historical
kubectl get deployment,statefulset,job,cronjob -A | grep prediction-generator-6548b78645-mzc6l
kubectl delete deployment trades-historical -n default
kubectl delete deployment trades-historical -n rwml
kubectl delete deployment prediction-generator-6548b78645-mzc6l -n rwml
CHECK NOTHING LEFT BEHIND
kubectl get all -A | grep trades-historical
kubectl logs -f prediction-generator-6548b78645-5nwsn -n rwml
kustomize build deployment/dev/training-pipeline | kubectl apply -f -


Rebuild the image:

docker build -t training-pipeline:dev -f docker/training-pipeline.Dockerfile .


Load it into the kind cluster:

kind load docker-image training-pipeline:dev --name rwml-34fa


Apply with Kustomize (to trigger the rollout if needed):

kustomize build deployments/dev/training-pipeline | kubectl apply -f -


If the tag remains training-pipeline:dev, Kubernetes may not restart the pod automatically — in that case, you can manually trigger a redeploy:

kubectl delete pod -l job-name=training-pipeline-aed2 -n rwml


or for cronjob jobs:

kubectl create job --from=cronjob/training-pipeline-aed2 manual-training-job -n rwml


Would you like me to show you how to make Kubernetes auto-pick the new image every time you build

[x]  kind load docker-image prediction-api:dev --name mlfund-2025
[x] kubectl rollout restart deployment prediction-api -n kafka



