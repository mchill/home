#!/bin/bash

helm repo add traefik https://helm.traefik.io/traefik
helm repo add longhorn https://charts.longhorn.io
helm repo add prometheus https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kustomize build sealed-secrets | kubectl apply --server-side -f -
kustomize build cert-manager | kubectl apply --server-side -f -
pushd traefik-external && helm upgrade --install --atomic --create-namespace -n traefik-external --version 20.1.1 --values values.yaml --post-renderer ../kustomize.sh traefik-external traefik/traefik && popd
pushd traefik-internal && helm upgrade --install --atomic --create-namespace -n traefik-internal --version 20.1.1 --values values.yaml --post-renderer ../kustomize.sh traefik-internal traefik/traefik && popd
kustomize build metallb | kubectl apply --server-side -f -
kustomize build kube-karp | kubectl apply --server-side -f -
pushd longhorn && helm upgrade --install --atomic --create-namespace -n longhorn-system --version 1.3.2 --values values.yaml --post-renderer ../kustomize.sh longhorn longhorn/longhorn && popd
pushd prometheus && helm upgrade --install --atomic --create-namespace -n monitoring --version 41.7.4 --values values.yaml --post-renderer ../kustomize.sh prometheus prometheus/kube-prometheus-stack && popd
pushd loki && helm upgrade --install --atomic -n monitoring --create-namespace --version 2.8.4 --values values.yaml --post-renderer ../kustomize.sh loki grafana/loki-stack && popd
kustomize build server | kubectl apply --server-side -f -
