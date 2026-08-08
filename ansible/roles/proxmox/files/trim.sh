#!/bin/bash

set -e;

VOLUME=$1;
echo "Trimming volume: $VOLUME";

WATCHERS=$(rbd status k8s/$VOLUME);
if echo "$WATCHERS" | grep -qE '^[[:space:]]*watcher='; then
    echo "ABORT: $VOLUME is still in use - scale the deployment down first";
    echo "$WATCHERS";
    exit 1;
fi

cleanup() {
    mkdir -p /mnt/$VOLUME;
    umount /mnt/$VOLUME > /dev/null 2>&1 || true;
    rbd device unmap k8s/$VOLUME > /dev/null 2>&1 || true;
}

trap cleanup EXIT;
cleanup;

# Trim filesystem
rbd device map k8s/$VOLUME;
mount /dev/rbd/k8s/$VOLUME /mnt/$VOLUME;
fstrim -v /mnt/$VOLUME;
rbd sparsify k8s/$VOLUME;
