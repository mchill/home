#!/bin/sh

cd /server
command -v getfacl || apk add acl
getfacl -R . > permissions.facl
rclone sync -lv --local-no-check-updated /server local:/backup
