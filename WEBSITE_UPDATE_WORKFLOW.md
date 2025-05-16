# TurnClicksToClients Website Update Workflow

This document outlines the standard process for making updates to the TurnClicksToClients website using GitHub for version control.

## Overview of the Workflow

1. **Create a Branch**: Start a new branch for your feature or fix
2. **Make Changes**: Implement your changes in this branch
3. **Test Changes**: Verify your changes work as expected
4. **Commit Changes**: Save your changes with descriptive messages
5. **Push to GitHub**: Upload your branch to GitHub
6. **Create Pull Request**: Request to merge your changes into the main branch
7. **Review and Merge**: Review the changes and merge the pull request

## Detailed Steps

### 1. Create a Branch

Always start with a fresh branch from the latest main:

```bash
# Make sure you're on main branch
git checkout main

# Get the latest changes
git pull

# Create a new branch with a descriptive name
git checkout -b feature-name
```

Branch naming conventions:
- `feature-*` for new features
- `fix-*` for bug fixes
- `update-*` for content updates
- `improve-*` for improvements to existing features

Examples:
- `feature-newsletter-signup`
- `fix-mobile-navigation`
- `update-pricing-page`
- `improve-page-load-speed`

### 2. Make Changes

Implement your changes in this branch. Keep changes focused on a single feature or fix to make reviews easier.

### 3. Test Changes

Before committing, always test your changes:
- Check on different browsers
- Test on mobile and desktop views
- Verify all links work
- Ensure images load properly

### 4. Commit Changes

Commit your changes with clear, descriptive messages:

```bash
# Add all changed files
git add .

# Or add specific files
git add file1.html file2.css

# Commit with a descriptive message
git commit -m "Fix mobile navigation menu on all pages"
```

Good commit messages:
- Start with a verb (Fix, Add, Update, Improve, Remove)
- Be specific about what changed
- Keep under 50 characters if possible
- Add details in the commit body if needed

### 5. Push to GitHub

Upload your branch to GitHub:

```bash
git push origin feature-name
```

### 6. Create Pull Request

Go to GitHub and create a pull request:
1. Navigate to https://github.com/elevateandautomate/turnclickstoclients
2. You should see a prompt to create a pull request for your recently pushed branch
3. Click "Compare & pull request"
4. Fill in the details:
   - Title: Brief description of changes
   - Description: More details, including:
     - What changed
     - Why it was changed
     - How to test the changes
     - Screenshots (if applicable)
5. Click "Create pull request"

### 7. Review and Merge

Review the changes in the pull request:
1. Check the "Files changed" tab to review all changes
2. Test the changes if possible
3. When satisfied, click "Merge pull request"
4. Click "Confirm merge"
5. (Optional) Delete the branch after merging

## Using the Helper Scripts

We've created helper scripts to streamline this process:

### Start a new feature

```bash
./scripts/start-feature.sh feature-name
```

This script:
- Ensures you're on the latest main
- Creates a new branch
- Sets up the basic structure

### Prepare for pull request

```bash
./scripts/prepare-pr.sh "Brief description of changes"
```

This script:
- Runs basic checks on your code
- Commits all changes with your message
- Pushes to GitHub
- Opens the pull request page

## Common Issues and Solutions

### Merge Conflicts

If you get merge conflicts:

1. Pull the latest main into your branch:
   ```bash
   git checkout main
   git pull
   git checkout your-branch
   git merge main
   ```

2. Resolve conflicts in the files
3. Commit the resolved conflicts:
   ```bash
   git add .
   git commit -m "Resolve merge conflicts"
   ```

### Reverting Changes

If you need to undo changes:

1. To undo uncommitted changes to a file:
   ```bash
   git checkout -- filename
   ```

2. To undo the last commit (but keep the changes):
   ```bash
   git reset --soft HEAD~1
   ```

3. To completely undo the last commit and changes:
   ```bash
   git reset --hard HEAD~1
   ```

## Best Practices

1. **Small, Focused Changes**: Keep pull requests small and focused on a single feature or fix
2. **Regular Updates**: Pull from main regularly to avoid large merge conflicts
3. **Descriptive Naming**: Use clear names for branches and descriptive commit messages
4. **Test Before Committing**: Always test your changes before committing
5. **Document Your Changes**: Include detailed descriptions in pull requests

## Need Help?

If you encounter any issues with this workflow, contact the development team for assistance.
