#!/bin/bash

kubectl kustomize plex && echo "---"
kubectl kustomize tautulli && echo "---"
