#!/bin/bash

unset -v
REBUILD_IMAGE="false"
DEVELOPMENT="false"

while getopts bd opt; do
	case "$opt" in
		b) REBUILD_IMAGE="true";;
		d) DEVELOPMENT="true";;
		*)
			echo "Unknown flag" >&2
			exit 1
	esac
done

shift "$(( OPTIND -1 ))"

COMMAND_STRING='BUILD_TIMESTAMP=$(date -u --rfc-3339=seconds) docker compose'

if $DEVELOPMENT; then
	COMMAND_STRING+=' -f compose.yml -f dev.compose.yml'
fi

COMMAND_STRING+=' up -d'

if $REBUILD_IMAGE; then
	COMMAND_STRING+=' --build'
fi

eval "$COMMAND_STRING"

