# Workflow Architecture

## Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         TRIGGER EVENTS                           │
├─────────────────────────────────────────────────────────────────┤
│  1. Manual (workflow_dispatch)                                  │
│  2. Scheduled (Every Sunday at midnight UTC)                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION                            │
└─────────────────────────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Checkout Repository  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Setup Node.js 18    │
         └───────────┬───────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UPDATE SCRIPT                               │
│  (.github/scripts/update-readme.js)                             │
├─────────────────────────────────────────────────────────────────┤
│  1. Fetch all repositories using GitHub CLI                     │
│     ├─> Filter: Remove archived repos                           │
│     ├─> Filter: Remove forks                                    │
│     └─> Filter: Remove portfolio repo itself                    │
│                                                                  │
│  2. For each repository:                                        │
│     ├─> Extract metadata (name, description, language)          │
│     ├─> Get stars and forks count                              │
│     ├─> Get latest release/tag version (if available)           │
│     └─> Get homepage URL (if available)                         │
│                                                                  │
│  3. Generate project cards:                                     │
│     ├─> Create badges (language, version, stars, forks)        │
│     ├─> Format description                                      │
│     └─> Add links (repository, demo)                            │
│                                                                  │
│  4. Update README.md:                                           │
│     ├─> Remove old projects section (if exists)                │
│     ├─> Insert new projects section                             │
│     └─> Write updated content                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Check for Changes    │
         │  (git diff)           │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    No Changes            Changes Detected
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────────────────────┐
│  Skip PR        │    │  Create Pull Request           │
│  Creation       │    │  - Title: 🤖 Update README     │
│                 │    │  - Branch: update/readme-auto-* │
│                 │    │  - Labels: automated, docs      │
│                 │    │  - Assignee: FlaviaMarcella     │
└─────────────────┘    └────────────┬────────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │   Pull Request   │
                          │   Created!       │
                          └──────────────────┘
```

## Component Details

### Input
- GitHub username: `FlaviaMarcella`
- Repository data from GitHub CLI
- Current README.md content

### Processing
1. **Data Collection**
   - Uses `gh repo list` to fetch repositories
   - Uses `gh release list` to get versions
   - Uses `gh api` to get tags as fallback

2. **Filtering**
   - Excludes archived repositories
   - Excludes forked repositories
   - Excludes the portfolio repository itself
   - Sorts by last updated date

3. **Badge Generation**
   - Language badge with logo (shields.io)
   - Version badge (if release/tag exists)
   - Stars count badge
   - Forks count badge

4. **Content Assembly**
   - Project section header
   - Last updated timestamp
   - Project cards for each repository
   - Repository links and demo links

### Output
- Updated README.md with projects section
- Pull request with changes (if any)
- Automated commit message
- Workflow logs for debugging

## Error Handling

```
Error During Execution
         │
         ▼
┌─────────────────────┐
│  Log Error Message  │
│  Exit with code 1   │
└─────────────────────┘
         │
         ▼
   Workflow Fails
   (Visible in Actions tab)
```

## Security Model

- ✅ Uses `GITHUB_TOKEN` (automatic, scoped)
- ✅ No external API calls
- ✅ Read-only access to repository data
- ✅ Write access only to own repository
- ✅ No secrets exposed in logs
- ✅ CodeQL verified (0 vulnerabilities)

## Maintenance

- **No maintenance required** for normal operation
- Review and merge generated pull requests
- Customize as needed via configuration files
- Monitor workflow runs in Actions tab
