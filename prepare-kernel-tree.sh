cut_line() {
    line=$1
    n=$2

    echo "$line" | tr -s $'\t' | cut -d $'\t' -f "$n"
}

while IFS='$\n' read -r line; do
    if [ -z "$line" ]; then
        continue
    fi

    if [ "$line" = "#*" ]; then
        continue
    fi

    url=$(cut_line "$line" 1)
    repo=$(cut_line "$line" 2)
    path=$(cut_line "$line" 3)
    commit=$(cut_line "$line" 4)

    git remote remove "$repo" &> /dev/null
    git remote add "$repo" "$url"
    git fetch -q "$repo" "$commit"

    if [ "$path" = "/" ]; then
        echo "Creating tree with $repo $commit"
        git reset --hard FETCH_HEAD
    else
        echo "Creating subtree at $path with $repo $commit"
        git subtree add -P "$path" FETCH_HEAD
    fi
done
