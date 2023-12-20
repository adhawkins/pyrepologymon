#!/usr/bin/env python3

import click
import requests
import sys

from packaging import version


def debugPrint(message, debug):
    if debug:
        print(message, file=sys.stderr)


@click.command()
@click.option("--maintainer", help="The maintainer", required=True)
@click.option("--repo", help="repo", default="alpine_edge")
@click.option("--debug/--no-debug", default=False, help="Debug")
def monitor(maintainer, repo, debug):
    request = (
        f"https://repology.org//api/v1/projects/?maintainer={maintainer}&inrepo={repo}"
    )

    debugPrint(f"Request: '{request}", debug)
    response = requests.get(request)

    if response.status_code == requests.codes.ok:
        packages = response.json()

        for package in packages.keys():
            debugPrint(f"Processing {package}", debug)

            highestVersion = None
            checkVersion = None

            for packageRepo in packages[package]:
                if "openpkg" not in packageRepo["repo"]:
                    debugPrint(
                        f"\tProcessing repo {packageRepo['repo']}, version: {packageRepo['version']}",
                        debug,
                    )

                    try:
                        repoVersion = version.parse(packageRepo["version"])

                        if not highestVersion or repoVersion > highestVersion:
                            highestVersion = repoVersion

                        if not checkVersion and packageRepo["repo"] == repo:
                            checkVersion = repoVersion

                    except version.InvalidVersion as e:
                        pass

            debugPrint(f"\tCheck: {checkVersion}, highest: {highestVersion}", debug)
            if checkVersion < highestVersion:
                print(
                    f"Package {package} out of date ({checkVersion} < {highestVersion})"
                )
    else:
        debugPrint(f"Status code: {data.status_code}", debug)


if __name__ == "__main__":
    monitor()
