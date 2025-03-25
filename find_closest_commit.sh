#!/bin/bash

STARTING_COMMIT="$1"
TARGET_COMMIT="$2"

PARENTS=$(git rev-list --parents "$STARTING_COMMIT" | cut -d ' ' -f2-)

echo "$PARENTS"

if [ -z "$PARENTS" ]; then
    echo "No parent commits found."
    exit 1
fi

BEST_PARENT=""
MIN_DIFF=""

for PARENT in $PARENTS; do
    DIFF_SIZE=$(git diff --numstat "$PARENT" "$TARGET_COMMIT" | awk '{s+=$1+$2} END {print s}')
    
    if [ -z "$MIN_DIFF" ] || [ "$DIFF_SIZE" -lt "$MIN_DIFF" ]; then
        MIN_DIFF=$DIFF_SIZE
        BEST_PARENT=$PARENT
        echo "Best parent commit: $BEST_PARENT with diff size: $MIN_DIFF"
    fi
done
