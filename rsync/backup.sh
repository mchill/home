#!/bin/sh

cd /backup
command -v getfacl || apk add acl
getfacl -R . > permissions.facl
ssh-keyscan -H nas >> ~/.ssh/known_hosts
rsync -av --delete /backup-before rsync@nas:/volume1/Server
