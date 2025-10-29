"""Minimal script to exercise the Adzuna Job Search API.

Replace the placeholder credentials with the `app_id` and `app_key`
you receive from https://developer.adzuna.com/ before running.
"""

from __future__ import annotations

import os
from typing import Any

import requests


def load_env(path: str = ".env") -> None:
    """Populate environment variables from a simple KEY=VALUE .env file."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def fetch_jobs(app_id: str, app_key: str) -> dict[str, Any]:
    """Call the Adzuna jobs search endpoint and return the response JSON."""
    endpoint = "https://api.adzuna.com/v1/api/jobs/sg/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 3,
        "what": "data scientist",
        "content-type": "application/json",
    }
    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    load_env()
    app_id = os.getenv("ADZUNA_APP_ID", "your_app_id")
    app_key = os.getenv("ADZUNA_APP_KEY", "your_app_key")

    if app_id == "your_app_id" or app_key == "your_app_key":
        print(
            "Update .env with your ADZUNA_APP_ID and ADZUNA_APP_KEY values "
            "before running."
        )
        return

    payload = fetch_jobs(app_id, app_key)

    count = payload.get("count", 0)
    jobs = payload.get("results", [])
    print(f"Total matching jobs: {count}")
    if not jobs:
        print("No jobs returned.")
        return

    for index, job in enumerate(jobs[:3], start=1):
        print(f"--- Result {index} ---")
        print(f"Title: {job.get('title')}")
        print(f"Company: {job.get('company', {}).get('display_name')}")
        print(f"Location: {job.get('location', {}).get('display_name')}")
        print(f"URL: {job.get('redirect_url')}")
        print()


if __name__ == "__main__":
    main()
