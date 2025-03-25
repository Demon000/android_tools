#!/usr/bin/env python3

from os import path
import sys
import requests
import xml.etree.ElementTree as ET
import argparse


def parse_manifest(server, repo, tag, projects):
    url = f"{server}/{repo}/-/raw/release/{tag}.xml"
    print(f'Downloading {url}', file=sys.stderr)
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.text)

    for image in root.findall(".//refs/image"):
        server = image.get("server")
        project = image.get("project")
        tag = image.get("tag")
        parse_manifest(server, project, tag, projects)

    remote_mapping = {
        remote.get("name"): remote.get("fetch") for remote in root.findall(".//remote")
    }

    default_remote = root.find(".//default")
    default_remote_name = None
    if default_remote is not None:
        default_remote_name = default_remote.get("remote")

    for proj in root.findall(".//project"):
        name = proj.get("name")
        remote = proj.get("remote") or default_remote_name
        revision = proj.get("revision")
        full_url = f"{remote_mapping.get(remote)}/{name}"
        projects.append((name, full_url, revision))


def print_index(projects, index, repos):
    for values in sorted(projects):
        project = values[0]

        found = False
        for repo in repos:
            repo_source = repo_target = repo

            if ':' in repo:
                repo_source, repo_target = repo.split(':')

            if project.endswith(f'/{repo_source}'):
                project = repo_target
                found = True
                break

        entry = f'["{project}"]="{values[index]}"'

        if found:
            print(f"\t{entry}")
        else:
            print(f"\t# ignored: {entry}")


def parse_and_print(base, repo, tag, repos):
    projects = []
    parse_manifest(base, repo, tag, projects)

    print("declare -A REPOS_TO_URL=(")
    print_index(projects, 1, repos)
    print(")")

    print()

    print("declare -A REPOS_TO_REF=(")
    print_index(projects, 2, repos)
    print(")")


def main():
    base = "https://git.codelinaro.org/clo"
    repo = "la/la/vendor/manifest"

    parser = argparse.ArgumentParser("Parse manifest and output modules data")
    parser.add_argument("tag", help="Tag")
    parser.add_argument("repos", nargs="+", help="Repos to process")

    args = parser.parse_args()

    parse_and_print(base, repo, args.tag, args.repos)

if __name__ == "__main__":
    main()
