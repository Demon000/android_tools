#! /bin/bash

adb wait-for-device root

FILE="$1"

if [[ -n "$FILE" ]] && [[ -f "$FILE" ]]; then
	rm "$FILE"
fi

while true; do
	if [[ -n "$FILE" ]]; then
		adb logcat -b all >> "$FILE"
	else
		adb logcat -b all
	fi
done
