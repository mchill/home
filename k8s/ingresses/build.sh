#!/bin/bash

kubectl kustomize ceph && echo "---"
kubectl kustomize kvm && echo "---"
kubectl kustomize nas && echo "---"
kubectl kustomize pdu && echo "---"
kubectl kustomize pihole && echo "---"
kubectl kustomize proxmox && echo "---"
kubectl kustomize unifi && echo "---"

kubectl kustomize remote/nas && echo "---"
kubectl kustomize remote/unifi && echo "---"
