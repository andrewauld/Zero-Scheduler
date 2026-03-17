#!/bin/zsh

echo "Setting up your cluster..."
kind create cluster --name ml-scheduler --config=config.yaml
echo ""
echo "Cluster created with one control plane node and three worker nodes."
echo ""

echo "Installing Knative..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.21.1/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.21.1/serving-core.yaml
kubectl apply -f https://github.com/knative-extensions/net-kourier/releases/download/knative-v1.21.0/kourier.yaml

echo ""
echo "Configuring Knative Serving to use Kourier"
kubectl patch configmap/config-network \
--namespace knative-serving \
--type merge \
--patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'

echo ""
echo "Configuring DNS for local access"
kubectl patch configmap/config-domain \
--namespace knative-serving \
--type merge \
--patch '{"data":{"127.0.0.1.sslip.io":""}}'

echo ""
echo "Getting external IP address"
kubectl --namespace kourier-system get service kourier

#echo ""
#echo "Configuring DNS"
#kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.21.1/serving-default-domain.yaml

echo ""
echo "Configuring HPA autoscaling..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.21.1/serving-hpa.yaml

echo ""
echo "Waiting for Knative to be ready..."
kubectl wait --for=condition=Ready pods --all -n knative-serving --timeout=300s

echo ""
echo "Installing Prometheus..."
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

echo ""
echo "Waiting for Prometheus to be ready..."
kubectl wait --for=condition=Ready pods --all -n monitoring --timeout=300s

echo ""
echo "Loading images..."
kind load docker-image kind.local/matrix-mult:v1 --name ml-scheduler
kind load docker-image kind.local/pass-hash:v1 --name ml-scheduler
kind load docker-image kind.local/prime-fact:v1 --name ml-scheduler

echo ""
echo "Deploying services..."
kubectl apply -f services/matrix_multiplication/matrix_service.yaml
kubectl apply -f services/password_hashing/password_service.yaml
kubectl apply -f services/prime_factorisation/prime_service.yaml

echo ""
echo "Cluster ready! Services have been deployed."

echo ""
echo "Remember to port forward Prometheus and Kourier in new terminals with:"
echo "kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "kubectl port-forward -n kourier-system service/kourier 8080:80"