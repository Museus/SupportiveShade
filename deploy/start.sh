#!/bin/bash

unset -v
REBUILD_IMAGE="false"

while getopts b opt; do
	case "$opt" in
		b) REBUILD_IMAGE="true";;
		*)
			echo "Unknown flag" >&2
			exit 1
	esac
done

shift "$(( OPTIND -1 ))"


if $REBUILD_IMAGE; then
	BUILD_TIMESTAMP=$(date -u --rfc-3339=seconds) docker compose up -d --build
else
	BUILD_TIMESTAMP=$(date -u --rfc-3339=seconds) docker compose up -d
fi

