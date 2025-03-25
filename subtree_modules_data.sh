#!/bin/bash

TARGET_DIR="qcom/opensource"

source "$1"

echo "$REPOS_TO_URL"

for REPO_NAME in "${!REPOS_TO_REF[@]}"; do
    REPO_REF="${REPOS_TO_REF[$REPO_NAME]}"
    REPO_URL="${REPOS_TO_URL[$REPO_NAME]}"
    REPO_DISK_PATH="$TARGET_DIR/$REPO_NAME"

    if [ ! -d "$REPO_DISK_PATH" ]; then
        REPO_DISK_DIR_PATH=$(dirname "$REPO_DISK_PATH")
        mkdir -p "$REPO_DISK_DIR_PATH"

        git subtree add --prefix="$REPO_DISK_PATH" "$REPO_URL" "$REPO_REF"
    else
        git subtree pull --prefix="$REPO_DISK_PATH" "$REPO_URL" "$REPO_REF"
    fi
done
