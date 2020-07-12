#!/bin/sh

cd /data/server
command -v getfacl || apk add acl
getfacl -R . > permissions.facl
rclone sync -lv --local-no-check-updated /data/server local:/data/backup
