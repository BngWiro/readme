import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta

USERNAME = "BngWiro"
README_FILE = "README.md"

START_MARKER = "<!-- REPOSITORIES:START -->"
END_MARKER = "<!-- REPOSITORIES:END -->"

WIB = timezone(timedelta(hours=7))


def get_repositories():
    repositories = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?type=owner&sort=updated&per_page=100&page={page}"
        )

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "BngWiro-Repository-Updater"
        }

        token = os.getenv("GITHUB_TOKEN")

        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def generate_table(repositories):
    repositories.sort(
        key=lambda repo: repo["name"].lower()
    )

    total = len(repositories)

    lines = [
        f"**Total Public Repositories: {total}**",
        "",
        "| Repository | Description | Language | Stars | Last Updated |",
        "|---|---|---|---:|---|"
    ]

    for repo in repositories:
        name = repo["name"]
        url = repo["html_url"]

        description = (
            repo.get("description") or "No description"
        ).replace("|", "\\|").replace("\n", " ")

        language = repo.get("language") or "-"

        stars = repo.get("stargazers_count", 0)

        updated = repo.get("updated_at", "")[:10]

        lines.append(
            f"| [{name}]({url}) "
            f"| {description} "
            f"| {language} "
            f"| {stars} "
            f"| {updated} |"
        )

    lines.extend([
        "",
        f"*Last synchronized: "
        f"{datetime.now(WIB).strftime('%d-%m-%Y %H:%M WIB')}*"
    ])

    return "\n".join(lines)


def update_readme(content):
    with open(README_FILE, "r", encoding="utf-8") as file:
        readme = file.read()

    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)

    if start == -1 or end == -1 or end < start:
        raise ValueError("README markers were not found.")

    start += len(START_MARKER)

    updated = (
        readme[:start]
        + "\n"
        + content
        + "\n"
        + readme[end:]
    )

    with open(README_FILE, "w", encoding="utf-8") as file:
        file.write(updated)


def main():
    print(f"Fetching repositories for {USERNAME}...")

    repositories = get_repositories()

    print(f"Found {len(repositories)} public repositories.")

    content = generate_table(repositories)

    update_readme(content)

    print("README successfully updated.")


if __name__ == "__main__":
    main()
