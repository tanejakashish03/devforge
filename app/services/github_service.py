import os

import requests


GITHUB_API_URL = "https://api.github.com"


def create_repository(name, description="", private=True):
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured")

    url = f"{GITHUB_API_URL}/user/repos"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    data = {
        "name": name,
        "description": description,
        "private": private,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30,
    )

    if response.status_code != 201:
        raise RuntimeError(
            f"GitHub repository creation failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()