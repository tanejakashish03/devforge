import os
import base64
from pathlib import Path

import logging
from urllib.parse import quote

import requests


GITHUB_API_URL = "https://api.github.com"


def get_github_headers():
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured")

    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10",
    }


def get_authenticated_user():
    headers = get_github_headers()

    url = f"{GITHUB_API_URL}/user"

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub user lookup failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


def get_repository(owner, repository_name):
    headers = get_github_headers()

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository_name}"
    )

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub repository lookup failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


def create_repository(name, description="", private=True):
    headers = get_github_headers()

    url = f"{GITHUB_API_URL}/user/repos"

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

    if response.status_code == 201:
        return {
            "status": "created",
            "repository": response.json(),
        }

    if response.status_code == 422:
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        repository_exists = any(
            error.get("field") == "name"
            and error.get("message")
            == "name already exists on this account"
            for error in error_data.get("errors", [])
        )

        if repository_exists:
            user = get_authenticated_user()

            repository = get_repository(
                owner=user["login"],
                repository_name=name,
            )

            return {
                "status": "exists",
                "repository": repository,
            }

    raise RuntimeError(
        f"GitHub repository creation failed: "
        f"{response.status_code} - {response.text}"
    )


def upload_file_to_repository(
    owner,
    repository_name,
    file_path,
    content,
):
    headers = get_github_headers()

    encoded_content = base64.b64encode(
        content.encode("utf-8")
    ).decode("utf-8")

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository_name}/contents/{file_path}"
    )

    data = {
        "message": f"Add {file_path}",
        "content": encoded_content,
    }

    existing_response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    if existing_response.status_code == 200:
        existing_file = existing_response.json()
        data["sha"] = existing_file["sha"]

    elif existing_response.status_code != 404:
        raise RuntimeError(
            f"GitHub file lookup failed: "
            f"{existing_response.status_code} - "
            f"{existing_response.text}"
        )

    response = requests.put(
        url,
        headers=headers,
        json=data,
        timeout=30,
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"GitHub file upload failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


def upload_project_directory(
    owner,
    repository_name,
    source_directory,
):
    source_directory = Path(source_directory)

    if not source_directory.exists():
        raise FileNotFoundError(
            f"Project directory not found: {source_directory}"
        )

    uploaded_files = []

    ignored_directories = {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
    }

    ignored_suffixes = {
        ".pyc",
        ".pyo",
    }

    # Upload .github files last so GitHub starts a single CI run, on a
    # commit that already contains every project file.
    all_files = sorted(
        source_directory.rglob("*"),
        key=lambda p: (
            ".github" in p.relative_to(source_directory).parts,
            p.as_posix(),
        ),
    )

    for file_path in all_files:
        if not file_path.is_file():
            continue

        if any(
            part in ignored_directories
            for part in file_path.parts
        ):
            continue

        if file_path.suffix in ignored_suffixes:
            continue

        relative_path = file_path.relative_to(
            source_directory
        )

        content = file_path.read_text(
            encoding="utf-8"
        )

        upload_file_to_repository(
            owner=owner,
            repository_name=repository_name,
            file_path=relative_path.as_posix(),
            content=content,
        )

        uploaded_files.append(
            relative_path.as_posix()
        )

    return uploaded_files


def delete_container_package(package_name):
    """Delete the GHCR package a project's CI published. Best effort.

    GitHub keeps a container package after its repo is deleted, and a new
    repo with the same name then cannot push to it. The Packages API
    rejects fine-grained tokens, so this uses PACKAGES_TOKEN, a classic
    token with only read:packages and delete:packages.
    """
    token = os.getenv("PACKAGES_TOKEN")

    if not token:
        logging.warning(
            "PACKAGES_TOKEN is not set; skipping cleanup of package %s",
            package_name,
        )
        return False

    url = (
        f"{GITHUB_API_URL}/user/packages/container/"
        f"{quote(package_name.lower(), safe='')}"
    )

    response = requests.delete(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2026-03-10",
        },
        timeout=30,
    )

    if response.status_code in (204, 404):  # deleted, or never existed
        return True

    logging.warning(
        "Could not delete package %s: %s %s",
        package_name,
        response.status_code,
        response.text,
    )
    return False


def delete_repository(owner, repository_name):
    try:
        delete_container_package(repository_name)
    except Exception:
        logging.exception("Package cleanup failed for %s", repository_name)

    return _delete_repository_only(owner, repository_name)


def _delete_repository_only(owner, repository_name):
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured")

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository_name}"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    response = requests.delete(
        url,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 204:
        raise RuntimeError(
            f"GitHub repository deletion failed: "
            f"{response.status_code} - {response.text}"
        )

    return True