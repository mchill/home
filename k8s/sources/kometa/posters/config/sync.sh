#!/bin/bash

BASE_DIR="/data"
RSYNC_OPTIONS=(-av --prune-empty-dirs --include='*/' --include='poster.*' --include='fanart.*' --include='theme.*' --exclude='*')

rsync ${RSYNC_OPTIONS[@]} $BASE_DIR/movies/sd/ $BASE_DIR/movies/assets
rsync ${RSYNC_OPTIONS[@]} $BASE_DIR/tv/sd/ $BASE_DIR/tv/assets
rsync ${RSYNC_OPTIONS[@]} $BASE_DIR/extras/sd/ $BASE_DIR/extras/assets

for d in $BASE_DIR/movies/sd/*/; do
    movie=$(basename "$d")
    rsync ${RSYNC_OPTIONS[@]} "$BASE_DIR/movies/assets/$movie/" "$d";
done

for d in $BASE_DIR/tv/sd/*/; do
    show=$(basename "$d")
    rsync ${RSYNC_OPTIONS[@]} "$BASE_DIR/tv/assets/$show/" "$d";
done

for d in $BASE_DIR/extras/sd/*/; do
    extra=$(basename "$d")
    rsync ${RSYNC_OPTIONS[@]} "$BASE_DIR/extras/assets/$extra/" "$d";
done
