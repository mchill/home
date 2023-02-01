#!/bin/bash

cat <&0 > helm.yaml
microk8s kubectl kustomize
rm helm.yaml
