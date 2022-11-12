#!/bin/bash

BASE_DIR="/data"
RSYNC_OPTIONS=(-av --prune-empty-dirs --include='*/' --include='poster.*' --include='fanart.*' --include='theme.*' --exclude='*')

rsync ${RSYNC_OPTIONS[@]} $BASE_DIR/movies/ $BASE_DIR/assets/movies
rsync ${RSYNC_OPTIONS[@]} $BASE_DIR/tv/ $BASE_DIR/assets/tv
rsync ${RSYNC_OPTIONS[@]} $BASE_DIR/extras/ $BASE_DIR/assets/extras

for d in $BASE_DIR/movies/*/; do
    movie=$(basename "$d")
    rsync ${RSYNC_OPTIONS[@]} "$BASE_DIR/assets/movies/$movie/" "$d";
done

for d in $BASE_DIR/tv/*/; do
    show=$(basename "$d")
    rsync ${RSYNC_OPTIONS[@]} "$BASE_DIR/assets/tv/$show/" "$d";
done

for d in $BASE_DIR/extras/*/; do
    extra=$(basename "$d")
    rsync ${RSYNC_OPTIONS[@]} "$BASE_DIR/assets/extras/$extra/" "$d";
done
