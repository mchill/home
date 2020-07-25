#!/bin/sh

cd /server
command -v getfacl || apk add acl
getfacl -R . > permissions.facl
ssh-keyscan -H nas >> ~/.ssh/known_hosts
rsync -av /backup rsync@nas:/volume1/Server
