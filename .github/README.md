# Automated README Update Documentation

## Overview

This automation automatically extracts details from all public repositories owned by FlaviaMarcella and updates the main README.md file with neat project cards.

## Features

- 🔄 Automatic repository data extraction using GitHub CLI
- 📊 Project cards with badges (language, stars, forks, version)
- 🎨 Professional formatting with shields.io badges
- 🕐 Runs on-demand or weekly schedule
- 🔀 Creates pull requests with updated README
- 🔍 Filters out archived repositories and forks
- 📝 Includes repository descriptions and links

## How It Works

### Workflow Triggers

The automation runs in two ways:

1. **On-Demand**: Manually trigger from GitHub Actions tab
   - Go to Actions → "Update README with Projects"
   - Click "Run workflow"
   
2. **Scheduled**: Automatically runs every Sunday at midnight UTC

### Workflow Process

1. Checks out the repository
2. Sets up Node.js environment
3. Executes the update script which:
   - Fetches all public repositories using GitHub CLI
   - Extracts metadata (language, description, stars, forks, etc.)
   - Retrieves latest release/tag version if available
   - Generates formatted project cards with badges
   - Updates README.md with the new content
4. Creates a pull request if changes are detected

### Project Card Format

Each repository is displayed as a card containing:

- **Title**: Repository name (linked)
- **Badges**: 
  - Language badge with logo
  - Version badge (if available)
  - Stars count
  - Forks count
- **Description**: Repository description or "No description available"
- **Links**:
  - Repository URL
  - Demo/Homepage URL (if available)

### Example Output

**With version badge:**

```markdown
### [project-name](https://github.com/FlaviaMarcella/project-name)

![C](https://img.shields.io/badge/C-blue?style=flat-square&logo=c) ![Version](https://img.shields.io/badge/version-v1.0.0-green?style=flat-square) ![Stars](https://img.shields.io/github/stars/FlaviaMarcella/project-name?style=flat-square) ![Forks](https://img.shields.io/github/forks/FlaviaMarcella/project-name?style=flat-square)

Description of the project goes here.

[📦 Repository](https://github.com/FlaviaMarcella/project-name) | [🌐 Demo](https://example.com)
```

**Without version badge:**

```markdown
### [project-name](https://github.com/FlaviaMarcella/project-name)

![C](https://img.shields.io/badge/C-blue?style=flat-square&logo=c) ![Stars](https://img.shields.io/github/stars/FlaviaMarcella/project-name?style=flat-square) ![Forks](https://img.shields.io/github/forks/FlaviaMarcella/project-name?style=flat-square)

Description of the project goes here.

[📦 Repository](https://github.com/FlaviaMarcella/project-name)
```

## Files

- **`.github/workflows/update-readme.yml`**: GitHub Actions workflow definition
- **`.github/scripts/update-readme.js`**: Node.js script that generates project cards

## Customization

### Modify Update Frequency

Edit `.github/workflows/update-readme.yml`:

```yaml
schedule:
  - cron: '0 0 * * 0'  # Current: Every Sunday at midnight UTC
```

Cron syntax examples:
- Daily: `'0 0 * * *'`
- Every Monday: `'0 0 * * 1'`
- First day of month: `'0 0 1 * *'`

### Customize Card Layout

Edit `.github/scripts/update-readme.js` in the `generateProjectCard()` function to modify:
- Badge styles
- Card formatting
- Additional metadata to display

### Filter Repositories

Modify the filter in the `updateReadme()` function:

```javascript
const filteredRepos = repos
  .filter(repo => !repo.isArchived && !repo.isFork && repo.name !== 'FlaviaMarcella.github.io')
  .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
```

## Troubleshooting

### Workflow Fails to Run

- Ensure the repository has Actions enabled
- Check that `GITHUB_TOKEN` permissions are set correctly in workflow file

### No Pull Request Created

- This is normal if no changes were detected
- Check the workflow logs for "No changes detected" message

### Script Errors

- Verify GitHub CLI is available in the runner (included by default in ubuntu-latest)
- Check that GITHUB_TOKEN environment variable is set

## Maintenance

The automation requires no regular maintenance. However, consider:

- Reviewing and merging generated pull requests
- Updating Node.js version in workflow if needed
- Customizing the card layout based on preference

## Support

For issues or questions, please open an issue in the repository.
