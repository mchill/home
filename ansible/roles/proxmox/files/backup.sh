#!/bin/bash

set -e;

VOLUME=$1;
echo "Backing up volume: $VOLUME";

cleanup() {
    mkdir -p /backup/$VOLUME;
    umount /backup/$VOLUME > /dev/null 2>&1 || true;
    rbd device unmap k8s/$VOLUME > /dev/null 2>&1 || true;
    rbd device unmap k8s/$VOLUME@backup > /dev/null 2>&1 || true;
    rbd snap remove k8s/$VOLUME@backup > /dev/null 2>&1 || true;
}

trap cleanup EXIT;
cleanup;

# Back up the image
rbd snap create k8s/$VOLUME@backup;
rbd device map --read-only k8s/$VOLUME@backup;
rsync -ahL --copy-devices /dev/rbd/k8s/$VOLUME@backup kubernetes@192.168.1.10:/volume1/Ceph/$VOLUME.img;

# Back up the filesystem
mount -o noload /dev/rbd/k8s/$VOLUME@backup /backup/$VOLUME;
getfacl -R /backup/$VOLUME > /backup/$VOLUME.facl;
rsync -ah /backup/$VOLUME.facl kubernetes@192.168.1.10:/volume1/Ceph;
rsync -ahv --delete-before /backup/$VOLUME kubernetes@192.168.1.10:/volume1/Ceph;
