#!/bin/bash

kubectl kustomize kvm && echo "---"
kubectl kustomize nas && echo "---"
kubectl kustomize pdu && echo "---"
kubectl kustomize pihole && echo "---"
kubectl kustomize unifi && echo "---"
