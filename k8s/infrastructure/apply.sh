#!/bin/bash

export HELM_PLUGINS=../../helm/plugins

curl -skSL https://raw.githubusercontent.com/kubernetes-csi/csi-driver-smb/v1.16.0/deploy/install-driver.sh | bash -s v1.16.0 --

helm repo add traefik https://helm.traefik.io/traefik
helm repo add ceph-csi https://ceph.github.io/csi-charts
helm repo add intel https://intel.github.io/helm-charts
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus https://prometheus-community.github.io/helm-charts
helm repo add grafana-community https://grafana-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

kubectl apply --server-side -k sealed-secrets
kubectl wait --for=condition=available --timeout=60s -n sealed-secrets deployment/sealed-secrets-controller
find ../ -type f -iname secret.yaml -not -path "*/charts/*" -execdir sh -c "cat {} | kubeseal --controller-namespace=sealed-secrets -o yaml > sealed-secret.yaml" \;

kubectl apply --server-side -k cert-manager
kubectl apply --server-side -k metallb
kubectl apply --server-side -k server
kubectl apply --server-side -k kube-vip

pushd traefik && helm upgrade --install --create-namespace -n traefik --version 27.0.2 --values values.yaml --post-renderer kustomize-renderer traefik traefik/traefik && popd
pushd ceph && helm upgrade --install --create-namespace -n ceph-csi-rbd --version 3.17.0 --values values.yaml --post-renderer kustomize-renderer ceph-csi-rbd ceph-csi/ceph-csi-rbd && popd
pushd intel && helm upgrade --install --create-namespace -n inteldeviceplugins-system --version 0.35.0 --post-renderer kustomize-renderer device-plugins-operator intel/intel-device-plugins-operator && popd
pushd argo && helm upgrade --install --create-namespace -n argo --version 1.0.14 --values values.yaml --post-renderer kustomize-renderer argo argo/argo-workflows && popd
pushd argocd && helm upgrade --install --create-namespace -n argocd --version 7.3.4 --values values.yaml --post-renderer kustomize-renderer argocd argo/argo-cd && popd

pushd prometheus && helm upgrade --install --create-namespace -n monitoring --version 82.15.0 --values values.yaml --post-renderer kustomize-renderer prometheus prometheus/kube-prometheus-stack && popd
pushd loki && helm upgrade --install --create-namespace -n monitoring --version 9.3.1 --values values.yaml loki grafana-community/loki && popd
pushd alloy && helm upgrade --install --create-namespace -n monitoring --version 1.6.2 --values values.yaml alloy grafana/alloy && popd
