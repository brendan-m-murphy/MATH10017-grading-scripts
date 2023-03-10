#! /bin/bash

outdir="$1"

latest_dl=$(ls -td ~/Downloads/gradebook_MATH10017* | head -1)

cp -r "${latest_dl}/" "$1"