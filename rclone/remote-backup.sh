#!/bin/sh

cd /server
command -v getfacl || apk add acl
getfacl -R . > permissions.facl
rclone dedupe --dedupe-mode newest encrypted:
rclone sync -lv --local-no-check-updated --fast-list /server encrypted:
