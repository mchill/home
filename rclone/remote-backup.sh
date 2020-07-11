#!/bin/sh

cd /data/server
command -v getfacl || apk add acl
getfacl -R . > permissions.facl
rclone sync -lv /data/server remote:server
