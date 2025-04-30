## Goals for today

- [x] Deploy Kafka in our dev kubernetes cluster.
- [x] Deploy the Kafka UI in our dev kubernetes cluster.

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

bashkubectl create namespace kafka

Install Strimzi Kafka operator:

bashkubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

Deploy Kafka cluster:
kubectl -n kafka port-forward svc/kafka-ui 8182:8080
bash
kubectl apply -f manifests/kafka-e11b.yaml -n kafka
Kafka UI Deployment

Deploy Kafka UI with the resource configuration to match your cluster:
kubectl apply -f kafka-ui.yaml -n kafka

Patch Kafka UI to reduce memory requirements (if facing resource constraints):

bashkubectl patch deployment kafka-ui -n kafka -p '{"spec":{"template":{"spec":{"containers":[{"name":"kafka-ui","resources":{"requests":{"memory":"256Mi"},"limits":{"memory":"512Mi"}}}]}}}}'

Expose Kafka UI with a LoadBalancer:

bashkubectl patch svc kafka-ui -n kafka -p '{"spec":{"type":"LoadBalancer"}}'

Get the external access information:

kubectl get svc kafka-ui -n kafka

Apply the updated configuration:

bash kubectl apply -f trades-deployment.yaml -n kafka

Check if the deployment was successful:

bashkubectl get deployment trades -n kafka

Check the pod status:

bashkubectl get pods -n kafka -l app=trades

If you need to view logs:

bashkubectl logs -f deployment/trades -n kafka

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