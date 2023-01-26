#!/bin/bash

helm repo add traefik https://helm.traefik.io/traefik
helm repo add longhorn https://charts.longhorn.io
helm repo add prometheus https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl apply --server-side -k sealed-secrets
find ../ -type f -iname secret.yaml -not -path "*/charts/*" -execdir sh -c "cat {} | kubeseal --controller-namespace=sealed-secrets -o yaml > sealed-secret.yaml" \;

kubectl apply --server-side -k cert-manager
kubectl apply --server-side -k metallb
kubectl apply --server-side -k kube-karp
kubectl apply --server-side -k server

pushd traefik-external && helm upgrade --install --atomic --create-namespace -n traefik-external --version 20.8.0 --values values.yaml --post-renderer ../kustomize.sh traefik-external traefik/traefik && popd
pushd traefik-internal && helm upgrade --install --atomic --create-namespace -n traefik-internal --version 20.8.0 --values values.yaml --post-renderer ../kustomize.sh traefik-internal traefik/traefik && popd
pushd longhorn && helm upgrade --install --atomic --create-namespace -n longhorn-system --version 1.4.0 --values values.yaml --post-renderer ../kustomize.sh longhorn longhorn/longhorn && popd
pushd prometheus && helm upgrade --install --atomic --create-namespace -n monitoring --version 44.3.0 --values values.yaml --post-renderer ../kustomize.sh prometheus prometheus/kube-prometheus-stack && popd
pushd loki && helm upgrade --install --atomic -n monitoring --create-namespace --version 2.8.9 --values values.yaml --post-renderer ../kustomize.sh loki grafana/loki-stack && popd
