#!/bin/zsh

echo "Setting up your cluster..."
kind create cluster --name ml-scheduler --config=config.yaml
echo ""
echo "Cluster created with one control plane node and three worker nodes."
echo ""

echo "Installing Knative..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.12.0/serving-core.yaml
kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.12.0/kourier.yaml

echo ""
echo "Loading images..."
kind load docker-image matrix-mult:v1 --name ml-scheduler
kind load docker-image pass-hash:v1 --name ml-scheduler
kind load docker-image prime-fact:v1 --name ml-scheduler

echo ""
echo "Cluster ready!"