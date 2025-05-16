# Git Quick Reference Guide

This guide provides a quick reference for common Git commands used in the TurnClicksToClients website workflow.

## Basic Commands

### Getting Started

```bash
# Clone the repository (first time only)
git clone https://github.com/elevateandautomate/turnclickstoclients.git

# Navigate to the repository
cd turnclickstoclients

# Check status
git status

# See current branch
git branch --show-current
```

### Branch Management

```bash
# List all local branches
git branch

# List all remote branches
git branch -r

# Create a new branch
git checkout -b branch-name

# Switch to an existing branch
git checkout branch-name

# Delete a local branch
git branch -d branch-name

# Delete a remote branch
git push origin --delete branch-name
```

### Making Changes

```bash
# Add all changes
git add .

# Add specific files
git add file1.html file2.css

# Commit changes
git commit -m "Your commit message"

# Push changes to GitHub
git push origin branch-name
```

### Getting Updates

```bash
# Update your current branch with latest changes
git pull

# Update a specific branch
git checkout branch-name
git pull origin branch-name

# Update your branch with changes from main
git checkout your-branch
git merge main
```

## Advanced Commands

### Viewing History

```bash
# View commit history
git log

# View commit history with graph
git log --graph --oneline --all

# View changes in a specific commit
git show commit-hash

# View changes between commits
git diff commit1..commit2
```

### Undoing Changes

```bash
# Discard changes in a file
git checkout -- file-name

# Undo the last commit (keep changes)
git reset --soft HEAD~1

# Undo the last commit (discard changes)
git reset --hard HEAD~1

# Revert a specific commit
git revert commit-hash
```

### Stashing Changes

```bash
# Save changes temporarily
git stash

# List stashed changes
git stash list

# Apply stashed changes
git stash apply

# Apply and remove stashed changes
git stash pop

# Clear all stashed changes
git stash clear
```

## Common Workflows

### Starting a New Feature

```bash
# Update main
git checkout main
git pull

# Create feature branch
git checkout -b feature-name

# Make changes...

# Commit and push
git add .
git commit -m "Implement feature"
git push origin feature-name

# Create pull request on GitHub
```

### Fixing a Bug

```bash
# Update main
git checkout main
git pull

# Create bug fix branch
git checkout -b fix-bug-name

# Make changes...

# Commit and push
git add .
git commit -m "Fix bug"
git push origin fix-bug-name

# Create pull request on GitHub
```

### Handling Merge Conflicts

```bash
# Update your branch with main
git checkout main
git pull
git checkout your-branch
git merge main

# If conflicts occur, edit the files to resolve them

# After resolving, commit the changes
git add .
git commit -m "Resolve merge conflicts"
```

## Using Our Helper Scripts

We've created helper scripts to streamline common tasks:

```bash
# Start a new feature
./scripts/start-feature.sh feature-name

# Prepare and submit a pull request
./scripts/prepare-pr.sh "Your commit message"

# Website maintenance tools
./scripts/website-tools.sh status
./scripts/website-tools.sh check-html
./scripts/website-tools.sh find-text "text to search"
```

## GitHub Pull Request Workflow

1. Push your branch to GitHub
2. Go to https://github.com/elevateandautomate/turnclickstoclients
3. Click "Compare & pull request"
4. Fill in the details
5. Click "Create pull request"
6. Review the changes
7. Click "Merge pull request"
8. Click "Confirm merge"
9. (Optional) Delete the branch

## Git Configuration Tips

```bash
# Set your username and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "code --wait"

# Create aliases for common commands
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
```

## Need Help?

If you encounter issues with Git, try these resources:
- Run `git --help` or `git command --help` for built-in documentation
- Visit [Git Documentation](https://git-scm.com/doc)
- Check [GitHub Guides](https://guides.github.com/)
- Ask a team member for assistance
