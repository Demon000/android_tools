#! /bin/bash

if [ $# -lt 2 ]; then
	echo "usage: cat modules-subdirs | $0 <repo-name> <base-name>"
	exit 1
fi

MODULES_REPO_NAME="$1"
BASE_NAME="$2"

base_name=""

merge_repo() {
	if [ -z "$base_name" ]; then
		echo "No paths found"
		exit 1
	fi

	branch_name="$BASE_NAME-$base_name"

	git fetch "$MODULES_REPO_NAME" "$branch_name"

	echo "Merging branch with name $branch_name"

	git merge --allow-unrelated-histories "$MODULES_REPO_NAME/$branch_name"

	base_name=""
}

while IFS='$\n' read -r subdir; do

	if [ -z "$base_name" ]; then
		base_name=$(basename "${subdir}" ".${subdir##*.}")
	fi

	if [ -n "$subdir" ]; then
		continue
	fi

	merge_repo
done

merge_repo
