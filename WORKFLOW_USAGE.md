# Quick Start: Automated README Update

## How to Trigger the Workflow

### Method 1: Manual Trigger (On-Demand)

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. In the left sidebar, click on **"Update README with Projects"**
4. Click the **"Run workflow"** button (top right)
5. Select the branch (usually `main`)
6. Click **"Run workflow"** to confirm

The workflow will:
- Fetch all your public repositories
- Generate project cards with badges
- Create a pull request with the updated README

### Method 2: Automatic (Weekly Schedule)

The workflow runs automatically **every Sunday at midnight UTC**. No action needed!

## What Happens Next?

1. The workflow runs and updates the README.md file
2. If changes are detected, a new pull request is created automatically
3. The PR will be titled: **"🤖 Update README with latest projects"**
4. Review the changes in the pull request
5. Merge the PR to update your README

## Checking Workflow Status

1. Go to **Actions** tab in your repository
2. Click on the latest workflow run
3. View logs to see what was processed
4. Check for any errors or issues

## Expected Output

The workflow will add a section like this to your README:

```markdown
## 📚 My Projects

> Automatically generated list of my public repositories. Last updated: 2025-11-24

### [file-manager](https://github.com/FlaviaMarcella/file-manager)

![C](https://img.shields.io/badge/C-blue?style=flat-square&logo=c) ![Version](https://img.shields.io/badge/version-v1.0.0-green?style=flat-square) ![Stars](https://img.shields.io/github/stars/FlaviaMarcella/file-manager?style=flat-square) ![Forks](https://img.shields.io/github/forks/FlaviaMarcella/file-manager?style=flat-square)

Este projeto contém um sistema de gerenciamento de arquivos em C...

[📦 Repository](https://github.com/FlaviaMarcella/file-manager) | [🌐 Demo](https://example.com)
```

## Troubleshooting

### No Pull Request Created
- This is normal if no changes were detected
- Check workflow logs for "No changes detected" message

### Workflow Failed
- Check the workflow logs in the Actions tab
- Ensure GitHub Actions is enabled for your repository
- Verify repository permissions are correctly set

### Need Help?
See `.github/README.md` for complete documentation.

## Customization

To modify the workflow:
- Edit `.github/workflows/update-readme.yml` for schedule/triggers
- Edit `.github/scripts/update-readme.js` for card layout/content

For detailed customization options, see `.github/README.md`.
