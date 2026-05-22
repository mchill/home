#!/bin/bash

set -euo pipefail
trap 'rm -f helm.yaml' EXIT

cat <&0 > helm.yaml
kubectl kustomize --enable-helm --load-restrictor=LoadRestrictionsNone
