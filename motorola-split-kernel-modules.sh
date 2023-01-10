#! /bin/bash

if [ $# -lt 2 ]; then
	echo "usage: cat modules-subdirs | $0 <base-name> <repo-name>"
	exit 1
fi

BASE_NAME="$1"
REPO_NAME="$2"

paths=""
path_params=""
base_name=""

base_commit=$(git rev-parse HEAD)

filter_repo() {
	if [ -z "$base_name" ] || [ -z "$path_params" ] || [ -z "$paths" ]; then
		echo "No paths found"
		exit 1
	fi

	echo -e "Creating subtree with name $base_name$paths\n"

	git filter-repo $path_params --refs HEAD

	branch_name="$BASE_NAME-$base_name"
	git branch -D "$branch_name"
	git checkout -b "$branch_name"
	git push -f --set-upstream "$REPO_NAME" "$branch_name"
	git checkout "$base_commit"
	paths=""
	path_params=""
	base_name=""
}

while IFS='$\n' read -r subdir; do
	if [ -z "$base_name" ]; then
		base_name=$(basename "${subdir}" ".${subdir##*.}")
	fi

	if [ -n "$subdir" ]; then
		paths="$paths\n$subdir"
		path_params="$path_params --path $subdir"
		continue
	fi

	filter_repo
done

filter_repo
