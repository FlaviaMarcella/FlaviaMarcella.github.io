#!/usr/bin/env python3
"""
Script to automatically update README.md with project cards from GitHub repositories.
"""

import os
import re
import sys
from typing import Dict, List, Optional
import requests


# Configuration
GITHUB_USER = "FlaviaMarcella"
GITHUB_API_BASE = "https://api.github.com"
PRIORITY_REPOS = ["Compilador_Simples", "file-manager", "Biblioteca_Sistema", "ElemHardSoft_Processor"]
README_PATH = "README.md"
SECTION_START_MARKER = "<!-- AUTO-GENERATED-PROJECTS-START -->"
SECTION_END_MARKER = "<!-- AUTO-GENERATED-PROJECTS-END -->"


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Warning: GITHUB_TOKEN not set. API rate limits will be lower.")
    return token


def make_github_request(url: str, token: Optional[str] = None) -> Optional[Dict]:
    """Make a request to GitHub API with authentication."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None


def get_user_repos(username: str, token: Optional[str]) -> List[Dict]:
    """Fetch all public repositories for a user."""
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{GITHUB_API_BASE}/users/{username}/repos?page={page}&per_page={per_page}&type=public"
        data = make_github_request(url, token)
        
        if not data:
            break
        
        if not data:  # Empty list
            break
            
        repos.extend(data)
        
        if len(data) < per_page:
            break
        
        page += 1
    
    return repos


def get_repo_languages(owner: str, repo_name: str, token: Optional[str]) -> Dict[str, int]:
    """Fetch language statistics for a repository."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/languages"
    return make_github_request(url, token) or {}


def get_latest_release(owner: str, repo_name: str, token: Optional[str]) -> Optional[Dict]:
    """Fetch the latest release for a repository."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/releases/latest"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    
    return None


def check_github_actions(owner: str, repo_name: str, token: Optional[str]) -> bool:
    """Check if repository has GitHub Actions workflows."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/contents/.github/workflows"
    data = make_github_request(url, token)
    return bool(data and isinstance(data, list) and len(data) > 0)


def get_primary_language(languages: Dict[str, int]) -> Optional[str]:
    """Get the primary language from language statistics."""
    if not languages:
        return None
    return max(languages.items(), key=lambda x: x[1])[0]


def create_language_badge(language: Optional[str]) -> str:
    """Create a shields.io badge for the primary language."""
    if not language:
        return ""
    
    # URL encode the language name
    encoded_lang = language.replace(" ", "%20")
    return f"![{language}](https://img.shields.io/badge/{encoded_lang}-blue?style=flat-square&logo=github)"


def create_release_badge(owner: str, repo_name: str, release: Optional[Dict]) -> str:
    """Create a release badge if a release exists."""
    if not release or not release.get("tag_name"):
        return ""
    
    tag = release["tag_name"]
    return f"[![Release](https://img.shields.io/github/v/release/{owner}/{repo_name}?style=flat-square)](https://github.com/{owner}/{repo_name}/releases/latest)"


def create_topics_badges(topics: List[str], max_topics: int = 5) -> str:
    """Create badges for repository topics (limited to max_topics)."""
    if not topics:
        return ""
    
    badges = []
    for topic in topics[:max_topics]:
        encoded_topic = topic.replace(" ", "%20").replace("-", "--")
        badges.append(f"![{topic}](https://img.shields.io/badge/{encoded_topic}-grey?style=flat-square)")
    
    return " ".join(badges)


def create_actions_badge(owner: str, repo_name: str, has_actions: bool) -> str:
    """Create GitHub Actions badge if workflows exist."""
    if not has_actions:
        return ""
    
    return f"[![Actions](https://img.shields.io/github/actions/workflow/status/{owner}/{repo_name}/main.yml?style=flat-square&label=actions)](https://github.com/{owner}/{repo_name}/actions)"


def create_repo_card(repo: Dict, token: Optional[str]) -> str:
    """Create a markdown card for a repository."""
    owner = repo["owner"]["login"]
    name = repo["name"]
    html_url = repo["html_url"]
    description = repo.get("description") or "—"
    homepage = repo.get("homepage")
    topics = repo.get("topics", [])
    license_info = repo.get("license")
    license_name = license_info["spdx_id"] if license_info else None
    
    # Fetch additional data
    languages = get_repo_languages(owner, name, token)
    primary_language = get_primary_language(languages)
    latest_release = get_latest_release(owner, name, token)
    has_actions = check_github_actions(owner, name, token)
    
    # Build card
    card = f"### [{name}]({html_url})\n\n"
    card += f"{description}\n\n"
    
    # Badges
    badges = []
    
    if primary_language:
        badges.append(create_language_badge(primary_language))
    
    if latest_release:
        badges.append(create_release_badge(owner, name, latest_release))
    
    if topics:
        badges.append(create_topics_badges(topics))
    
    # Note: GitHub Actions badge might not work for all repos, so we skip it for simplicity
    # if has_actions:
    #     badges.append(create_actions_badge(owner, name, has_actions))
    
    if badges:
        card += " ".join(badges) + "\n\n"
    
    # Quick info line
    info_parts = []
    
    if homepage:
        info_parts.append(f"🔗 [Demo]({homepage})")
    
    info_parts.append(f"📚 [Docs]({html_url}#readme)")
    
    if license_name and license_name != "NOASSERTION":
        info_parts.append(f"📄 {license_name}")
    
    if info_parts:
        card += " | ".join(info_parts) + "\n"
    
    card += "\n---\n"
    
    return card


def sort_repos(repos: List[Dict]) -> List[Dict]:
    """Sort repositories with priority repos first, then by stars."""
    priority = []
    others = []
    
    for repo in repos:
        if repo["name"] in PRIORITY_REPOS:
            priority.append(repo)
        else:
            others.append(repo)
    
    # Sort priority repos by the order in PRIORITY_REPOS
    priority_sorted = sorted(
        priority,
        key=lambda r: PRIORITY_REPOS.index(r["name"]) if r["name"] in PRIORITY_REPOS else len(PRIORITY_REPOS)
    )
    
    # Sort others by stargazers_count descending
    others_sorted = sorted(others, key=lambda r: r.get("stargazers_count", 0), reverse=True)
    
    return priority_sorted + others_sorted


def generate_projects_section(repos: List[Dict], token: Optional[str]) -> str:
    """Generate the complete projects section with all repo cards."""
    section = f"{SECTION_START_MARKER}\n\n"
    section += "## 📂 My Projects\n\n"
    section += "Here are all my public repositories, automatically updated weekly:\n\n"
    
    sorted_repos = sort_repos(repos)
    
    for repo in sorted_repos:
        section += create_repo_card(repo, token)
    
    section += f"\n{SECTION_END_MARKER}\n"
    
    return section


def update_readme(projects_section: str) -> bool:
    """Update README.md with the projects section."""
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {README_PATH} not found")
        return False
    
    # Check if markers exist
    if SECTION_START_MARKER in content and SECTION_END_MARKER in content:
        # Replace content between markers
        pattern = f"{re.escape(SECTION_START_MARKER)}.*?{re.escape(SECTION_END_MARKER)}"
        new_content = re.sub(pattern, projects_section.strip(), content, flags=re.DOTALL)
    else:
        # Append before footer (before last img tag with waving footer)
        footer_pattern = r'(<img width=100% src="https://capsule-render\.vercel\.app/api\?type=waving[^>]*>)'
        if re.search(footer_pattern, content):
            new_content = re.sub(
                footer_pattern,
                f"\n{projects_section}\n\\1",
                content
            )
        else:
            # Append at the end
            new_content = content.rstrip() + "\n\n" + projects_section
    
    # Write updated content
    try:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error writing to {README_PATH}: {e}")
        return False


def main():
    """Main function to orchestrate the README update."""
    print(f"Fetching repositories for user: {GITHUB_USER}")
    
    token = get_github_token()
    repos = get_user_repos(GITHUB_USER, token)
    
    if not repos:
        print("No repositories found or error fetching repositories.")
        sys.exit(1)
    
    print(f"Found {len(repos)} repositories")
    
    projects_section = generate_projects_section(repos, token)
    
    if update_readme(projects_section):
        print("✓ README.md updated successfully!")
    else:
        print("✗ Failed to update README.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
