#! /usr/bin/python

###############################################################################
# Query for the latest versions of rclone, plex_autoscan, and s6-overlay
###############################################################################
import docker
import json
import os
import requests
import sys
from git import Repo

old_versions = {}
current_versions = {}

client = docker.from_env()
try:
    old_versions['rclone_release_name'] = client.containers.run(
        os.environ['GITHUB_REPOSITORY'], command='rclone version', auto_remove=True, entrypoint='').decode('UTF-8').split('\n')[0].split(' ')[1].strip()
    old_versions['plex_autoscan_commit_ref'] = client.containers.run(
        os.environ['GITHUB_REPOSITORY'], command='git --work-tree=/opt/plex_autoscan rev-parse HEAD', auto_remove=True, entrypoint='').decode('UTF-8').strip()
    old_versions['alpine-plex_autoscan_commit_ref'] = client.images.get(
        os.environ['GITHUB_REPOSITORY']).labels['org.label-schema.vcs-ref']
    old_versions['s6_release'] = client.containers.run(
        os.environ['GITHUB_REPOSITORY'], command='cat /etc/S6_RELEASE', auto_remove=True, entrypoint='').decode('UTF-8').strip()
    print("Detected image versions:\n" + json.dumps(old_versions, indent=2))
except docker.errors.ContainerError as e:
    print(e)

current_versions['rclone_release_name'] = requests.get(
    'https://api.github.com/repos/rclone/rclone/releases/latest').json()["tag_name"]
current_versions['plex_autoscan_commit_ref'] = requests.get(
    'https://api.github.com/repos/l3uddz/plex_autoscan/commits/develop').json()["sha"]
current_versions['alpine-plex_autoscan_commit_ref'] = Repo(
    '.').commit('HEAD').hexsha
current_versions['s6_release'] = requests.get(
    'https://api.github.com/repos/just-containers/s6-overlay/releases/latest').json()["tag_name"]

print("Current detected versions:\n" + json.dumps(current_versions, indent=2))

if old_versions == current_versions:
    print("No version change, skipping image rebuild.")
    print("::set-output name=build::false")
else:
    print("Upstream versions changed.")
    print("::set-output name=build::true")

sys.exit(0)
