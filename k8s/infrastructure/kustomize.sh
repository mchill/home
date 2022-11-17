#!/bin/bash

cat <&0 > helm.yaml
kustomize build .
rm helm.yaml
