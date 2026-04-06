#!/bin/zsh

ML_EXTENDER=${1:-false}

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
kind load docker-image kind.local/fanout-func:v1 --name ml-scheduler
kind load docker-image kind.local/ml-extender:v1 --name ml-scheduler

echo ""
echo "Deploying services..."
kubectl apply -f services/matrix_multiplication/matrix_service.yaml
kubectl apply -f services/password_hashing/password_service.yaml
kubectl apply -f services/prime_factorisation/prime_service.yaml
kubectl apply -f services/fanout/fanout_service.yaml

if [ "$ML_EXTENDER" = "true" ]; then
  echo ""
  echo "Using ML-extended scheduler"
  echo ""
  echo "Deploying ML extender..."
  kubectl apply -f extender/ml-extender-deployment.yaml
  kubectl wait --for=condition=Ready pods -l app=ml-extender -n kube-system --timeout=120s

  EXTENDER_IP=$(kubectl get svc ml-extender -n kube-system -o jsonpath='{.spec.clusterIP}')
  sed -i '' "s|urlPrefix:.*|urlPrefix: \"http://$EXTENDER_IP:8080\"|" ml-scheduler-config.yaml

  echo ""
  echo "Configuring scheduler extender..."
  docker cp ml-scheduler-config.yaml ml-scheduler-control-plane:/etc/kubernetes/ml-scheduler-config.yaml

  docker cp inject_flag.py ml-scheduler-control-plane:/etc/kubernetes/inject_flag.py
  docker exec ml-scheduler-control-plane python3 /etc/kubernetes/inject_flag.py
  docker cp inject_mount.py ml-scheduler-control-plane:/etc/kubernetes/inject_mount.py
  docker exec ml-scheduler-control-plane python3 /etc/kubernetes/inject_mount.py

  echo ""
  echo "Waiting for scheduler to restart..."
  kubectl wait --for=condition=Ready pods -l component=kube-scheduler -n kube-system --timeout=60s
else
  echo ""
  echo "Using default scheduler"
fi

echo ""
echo "Cluster ready! Services have been deployed."

echo ""
echo "Remember to port forward Prometheus and Kourier in new terminals with:"
echo "kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "kubectl port-forward -n kourier-system service/kourier 8080:80"
echo ""