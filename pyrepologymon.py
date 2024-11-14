#!/usr/bin/env python3

import click
import logging
import requests
import sys

from packaging import version


@click.command()
@click.option("--maintainer", help="The maintainer", required=True)
@click.option("--repo", help="repo", default="alpine_edge")
@click.option("--debug/--no-debug", default=False, help="Debug")
def monitor(maintainer, repo, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    request = (
        f"https://repology.org/api/v1/projects/?maintainer={maintainer}&inrepo={repo}"
    )

    headers = {
        'User-Agent': 'pyrepologymon https://github.com/adhawkins/pyrepologymon'
    }

    logging.debug(f"Request: '{request}")
    response = requests.get(request, headers=headers)

    if response.status_code == requests.codes.ok:
        packages = response.json()

        for package in packages.keys():
            logging.debug(f"Processing {package}")

            highestVersion = None
            checkVersion = None

            for packageRepo in packages[package]:
                if "openpkg" not in packageRepo["repo"]:
                    logging.debug(
                        f"\tProcessing repo {packageRepo['repo']}, version: {packageRepo['version']}",
                    )

                    try:
                        repoVersion = version.parse(packageRepo["version"])

                        if not highestVersion or repoVersion > highestVersion:
                            highestVersion = repoVersion

                        if not checkVersion and packageRepo["repo"] == repo:
                            checkVersion = repoVersion

                    except version.InvalidVersion as e:
                        pass

            logging.debug(
                f"\tCheck: {checkVersion}, highest: {highestVersion}")
            if checkVersion < highestVersion:
                print(
                    f"Package {package} out of date ({checkVersion} < {highestVersion})"
                )
    else:
        print(f"Request error, status code: {response.status_code}")


if __name__ == "__main__":
    monitor()
