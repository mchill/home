#!/bin/bash

curl -skSL https://raw.githubusercontent.com/kubernetes-csi/csi-driver-smb/v1.16.0/deploy/install-driver.sh | bash -s v1.16.0 --

kubectl apply --server-side -k sealed-secrets
kubectl wait --for=condition=available --timeout=60s -n sealed-secrets deployment/sealed-secrets-controller
find ../ -type f -iname secret.yaml -not -path "*/charts/*" -execdir sh -c "cat {} | kubeseal --controller-namespace=sealed-secrets -o yaml > sealed-secret.yaml" \;

kubectl apply --server-side -k server
