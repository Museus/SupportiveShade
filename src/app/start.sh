#!/bin/bash

unset -v
LOCAL="false"

while getopts l opt; do
	case "$opt" in
		l) LOCAL="true";;
		*)
			echo "Unknown flag" >&2
			exit 1
	esac
done

shift "$(( OPTIND -1 ))"

source ./prestart.sh

echo "-- Starting Supportive Shade..."

API_TOKEN=$API_TOKEN python3 main.py

