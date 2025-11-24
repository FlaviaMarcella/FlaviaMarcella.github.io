const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const GITHUB_USERNAME = 'FlaviaMarcella';
const README_PATH = path.join(__dirname, '../../README.md');

/**
 * Execute a shell command and return the output
 */
function exec(command, env = {}) {
  try {
    return execSync(command, { 
      encoding: 'utf8', 
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, ...env }
    });
  } catch (error) {
    console.error(`Command failed: ${command}`);
    console.error(error.stderr || error.message);
    return null;
  }
}

/**
 * Get all public repositories for a user using GitHub CLI
 */
function getRepositories(username) {
  // Set GH_TOKEN from environment if available
  const env = process.env.GITHUB_TOKEN ? { GH_TOKEN: process.env.GITHUB_TOKEN } : {};
  
  const command = `gh repo list ${username} --json name,description,url,homepageUrl,primaryLanguage,stargazerCount,forkCount,isArchived,updatedAt,isFork --limit 1000`;
  const output = exec(command, env);
  
  if (!output) {
    throw new Error('Failed to fetch repositories');
  }
  
  return JSON.parse(output);
}

/**
 * Get the latest release/tag for a repository using GitHub CLI
 */
function getLatestRelease(username, repoName) {
  const env = process.env.GITHUB_TOKEN ? { GH_TOKEN: process.env.GITHUB_TOKEN } : {};
  
  try {
    const command = `gh release list -R ${username}/${repoName} --limit 1 --json tagName`;
    const output = exec(command, env);
    
    if (output) {
      const releases = JSON.parse(output);
      if (releases.length > 0) {
        return releases[0].tagName;
      }
    }
  } catch (error) {
    // No release found
  }
  
  // Try to get tags if no release
  try {
    const command = `gh api repos/${username}/${repoName}/tags --jq '.[0].name'`;
    const output = exec(command, env);
    return output ? output.trim() : null;
  } catch {
    return null;
  }
}

/**
 * Generate project card for a repository
 */
function generateProjectCard(repo, version) {
  const language = repo.primaryLanguage?.name || null;
  const languageBadge = language 
    ? `![${language}](https://img.shields.io/badge/${encodeURIComponent(language)}-blue?style=flat-square&logo=${getLanguageLogo(language)})` 
    : '';
  
  const versionBadge = version 
    ? `![Version](https://img.shields.io/badge/version-${encodeURIComponent(version)}-green?style=flat-square)` 
    : '';
  
  const starsBadge = `![Stars](https://img.shields.io/github/stars/${GITHUB_USERNAME}/${repo.name}?style=flat-square)`;
  const forksBadge = `![Forks](https://img.shields.io/github/forks/${GITHUB_USERNAME}/${repo.name}?style=flat-square)`;
  
  const description = repo.description || 'No description available';
  const repoUrl = repo.url;
  const homepageLink = repo.homepageUrl ? `[🌐 Demo](${repo.homepageUrl})` : '';
  
  let card = `### [${repo.name}](${repoUrl})\n\n`;
  card += `${languageBadge} ${versionBadge} ${starsBadge} ${forksBadge}\n\n`;
  card += `${description}\n\n`;
  card += `[📦 Repository](${repoUrl})`;
  if (homepageLink) {
    card += ` | ${homepageLink}`;
  }
  card += '\n\n';
  
  return card;
}

/**
 * Get logo identifier for shields.io badge based on language
 */
function getLanguageLogo(language) {
  const logoMap = {
    'JavaScript': 'javascript',
    'TypeScript': 'typescript',
    'Python': 'python',
    'Java': 'java',
    'C': 'c',
    'C++': 'cplusplus',
    'C#': 'csharp',
    'Go': 'go',
    'Rust': 'rust',
    'Ruby': 'ruby',
    'PHP': 'php',
    'HTML': 'html5',
    'CSS': 'css3',
    'Shell': 'gnu-bash',
    'Dart': 'dart',
    'Kotlin': 'kotlin',
    'Swift': 'swift'
  };
  
  return logoMap[language] || 'code';
}

/**
 * Update README with project cards
 */
function updateReadme() {
  console.log('Fetching repositories...');
  const repos = getRepositories(GITHUB_USERNAME);
  
  // Filter out the portfolio repository itself, archived repos, and forks
  const filteredRepos = repos
    .filter(repo => !repo.isArchived && !repo.isFork && repo.name !== 'FlaviaMarcella.github.io')
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  
  console.log(`Found ${filteredRepos.length} active repositories`);
  
  // Generate project cards
  let projectsSection = '## 📚 My Projects\n\n';
  projectsSection += `> Automatically generated list of my public repositories. Last updated: ${new Date().toISOString().split('T')[0]}\n\n`;
  
  for (const repo of filteredRepos) {
    console.log(`Processing: ${repo.name}`);
    const version = getLatestRelease(GITHUB_USERNAME, repo.name);
    projectsSection += generateProjectCard(repo, version);
  }
  
  // Read current README
  const currentReadme = fs.readFileSync(README_PATH, 'utf8');
  
  // Find the insertion point (before the contacts section)
  const contactsSectionMatch = currentReadme.match(/^## Contacts:/m);
  
  let newReadme;
  if (contactsSectionMatch) {
    // Insert projects section before contacts
    const insertIndex = contactsSectionMatch.index;
    const beforeContacts = currentReadme.substring(0, insertIndex);
    const fromContacts = currentReadme.substring(insertIndex);
    
    // Remove old projects section if it exists (match from header to next --- or ## header)
    const cleanedBefore = beforeContacts.replace(/## 📚 My Projects[\s\S]*?(?=\n---|^##|\n$)/m, '').trim();
    
    newReadme = cleanedBefore + '\n\n---\n\n' + projectsSection + '\n---\n\n' + fromContacts;
  } else {
    // Append at the end if no contacts section found
    newReadme = currentReadme.trim() + '\n\n---\n\n' + projectsSection;
  }
  
  // Write updated README
  fs.writeFileSync(README_PATH, newReadme);
  console.log('README.md updated successfully!');
}

// Run the update
try {
  updateReadme();
} catch (error) {
  console.error('Error updating README:', error);
  process.exit(1);
}
