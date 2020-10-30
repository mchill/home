## Sealed Secrets

Create a secret mapping environment variable names to base64 values. Decode like below.

`echo -n "secret" | base64 -w 0`

Then create a sealed secret from the secret. Be sure to specify the correct namespace, or else the secret won't be decryptable.

`kubeseal <secret.yaml >sealedsecret.yaml -o yaml -n kube-system`

## Deploy

```bash
kustomize build | microk8s kubectl apply -f - --prune -l prune=true --dry-run=client
microk8s kubectl delete --all ingressroute -n server
microk8s kubectl delete --all middleware -n server
kustomize build | microk8s kubectl apply -f - --prune -l prune=true
```

## Reset Cluster

```bash
sudo snap remove microk8s
sudo snap install microk8s --classic
microk8s enable storage
microk8s enable rbac
microk8s enable dns
```

You'll also have to regenerate all sealed secrets, now that the decryption key is different.
