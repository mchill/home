#!/bin/sh

cd /data/server
getfacl -R . > permissonions.facl
rclone sync -l --progress --stats-one-line /data/server remote:server
