# Automated README Update Script

This directory contains the automation script for updating the main README.md with project cards from all public repositories.

## Overview

The `update_readme.py` script automatically:
- Fetches all public repositories from the GitHub user "FlaviaMarcella"
- Generates markdown cards with badges and links for each repository
- Updates the README.md file with the latest repository information

## How It Works

### Repository Data Collection
The script uses the GitHub REST API to collect:
- Repository name, description, and URL
- Homepage link (if available)
- Topics/tags
- License information
- Primary programming language (via `/repos/{owner}/{repo}/languages` endpoint)
- Latest release information (if available)
- Presence of GitHub Actions workflows

### Card Generation
For each repository, the script creates a markdown card containing:
- **Title**: Repository name linked to the GitHub repo
- **Description**: Repo description or "—" if empty
- **Badges**: 
  - Primary language badge (shields.io)
  - Latest release version badge (if releases exist)
  - Topic badges (up to 5 topics)
- **Quick Links**:
  - 🔗 Demo: Link to homepage if available
  - 📚 Docs: Link to repository README
  - 📄 License: License type if specified

### Repository Ordering
Repositories are displayed in the following order:
1. **Priority repos** (if they exist):
   - Compilador_Simples
   - file-manager
   - Biblioteca_Sistema
   - ElemHardSoft_Processor
2. **All other repos** sorted by star count (descending)

### README Update
The script updates the section between these HTML markers:
```html
<!-- AUTO-GENERATED-PROJECTS-START -->
...generated content...
<!-- AUTO-GENERATED-PROJECTS-END -->
```

If the markers don't exist, the script appends the section before the footer.

## Usage

### Local Testing
```bash
# Requires Python 3.x and requests library
pip install requests

# Set GitHub token (optional but recommended to avoid rate limits)
export GITHUB_TOKEN="your_github_token"

# Run the script
python scripts/update_readme.py
```

### Automated Execution
The script runs automatically via GitHub Actions:
- **Weekly**: Every Monday at 6 AM UTC
- **Manual**: Via workflow_dispatch trigger in GitHub Actions

When run by GitHub Actions, it will:
1. Fetch the latest repository data
2. Update README.md
3. Create a pull request with the changes (if any)

## Configuration

Key configuration constants in `update_readme.py`:
- `GITHUB_USER`: GitHub username (default: "FlaviaMarcella")
- `PRIORITY_REPOS`: List of repos to display first
- `SECTION_START_MARKER`: HTML comment marking section start
- `SECTION_END_MARKER`: HTML comment marking section end

## Requirements

- Python 3.x
- `requests` library

## Error Handling

The script gracefully handles:
- API rate limits (with informative warnings)
- Missing or empty data fields
- Repositories without releases, topics, or licenses
- Network errors and API failures

## Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token for API authentication
  - Not required but highly recommended
  - Provides higher API rate limits
  - Automatically available in GitHub Actions
