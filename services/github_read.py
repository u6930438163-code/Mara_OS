"""Read-only GitHub integration. Never execute code returned by GitHub."""
import json
import os
import re
import urllib.error
import urllib.request

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")

class GitHubError(RuntimeError):
    pass

def repo_info(full_name):
    if not isinstance(full_name, str) or not REPO_PATTERN.fullmatch(full_name):
        raise ValueError("Invalid repository name")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Mara_OS"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request("https://api.github.com/repos/" + full_name, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.load(res)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as exc:
        raise GitHubError("GitHub repository lookup failed") from exc
    return {"name": data.get("full_name"), "description": data.get("description"),
            "default_branch": data.get("default_branch"), "url": data.get("html_url"),
            "private": data.get("private")}
