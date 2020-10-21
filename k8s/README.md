## Sealed Secrets

Create a secret mapping environment variable names to base64 values. Decode like below.

`echo -n "secret" | base64 -w 0`

Then create a sealed secret from the secret. Be sure to specify the correct namespace, or else the secret won't be decryptable.

`kubeseal <secret.yaml >sealedsecret.yaml -o yaml -n kube-system`

## Deploy

First, do a dry run to make sure the changes look okay. Run the following from the root directory.

`microk8s kubectl apply -k . --prune -l prune=true --dry-run=client`

If everything looks right, go ahead and deploy.

`microk8s kubectl apply -k . --prune -l prune=true --dry-run=client`
