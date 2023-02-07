#!/bin/bash

cat <&0 > helm.yaml
kubectl kustomize
rm helm.yaml
