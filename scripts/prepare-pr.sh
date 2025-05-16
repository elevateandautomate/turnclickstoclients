#!/bin/bash

# Script to prepare and submit a pull request for website updates

# Display help if help flag
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  echo "Usage: ./scripts/prepare-pr.sh \"Your commit message\""
  echo ""
  echo "This script will:"
  echo "  1. Check for common issues in your changes"
  echo "  2. Commit all changes with your message"
  echo "  3. Push to GitHub"
  echo "  4. Open the pull request page"
  echo ""
  echo "Example:"
  echo "  ./scripts/prepare-pr.sh \"Fix mobile navigation menu on all pages\""
  exit 0
fi

# Get commit message from argument
COMMIT_MESSAGE=$1

# Check if commit message is provided
if [ "$COMMIT_MESSAGE" == "" ]; then
  echo "Error: Commit message is required."
  echo "Usage: ./scripts/prepare-pr.sh \"Your commit message\""
  exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ $? -ne 0 ] || [ "$CURRENT_BRANCH" == "" ]; then
  echo "Error: Failed to get current branch."
  echo "Make sure you're in a git repository."
  exit 1
fi

# Check if we're on main branch
if [ "$CURRENT_BRANCH" == "main" ]; then
  echo "Error: You're on the main branch."
  echo "You should create a feature branch for your changes."
  echo "Run: ./scripts/start-feature.sh <branch-name>"
  exit 1
fi

# Basic checks for common issues
echo "Running basic checks..."

# Check for broken HTML tags
echo "Checking for broken HTML tags..."
grep -r --include="*.html" -l "<[a-z]\+[^>]*>[^<]*$" .
if [ $? -eq 0 ]; then
  echo "Warning: Possible broken HTML tags found in the files above."
  echo "Please check these files before continuing."
  read -p "Continue anyway? (y/n): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then
    echo "Aborting. Please fix the issues and try again."
    exit 1
  fi
fi

# Check for large files
echo "Checking for large files..."
find . -type f -size +5M | grep -v "\.git/"
if [ $? -eq 0 ]; then
  echo "Warning: Large files found (>5MB)."
  echo "Consider optimizing these files or using external hosting."
  read -p "Continue anyway? (y/n): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then
    echo "Aborting. Please address the large files and try again."
    exit 1
  fi
fi

# Show status before committing
echo ""
echo "Current status:"
git status

# Confirm before proceeding
echo ""
echo "Ready to commit all changes with message:"
echo "\"$COMMIT_MESSAGE\""
read -p "Continue? (y/n): " CONTINUE
if [ "$CONTINUE" != "y" ]; then
  echo "Aborting. No changes were committed."
  exit 1
fi

# Commit changes
echo "Committing changes..."
git add .
git commit -m "$COMMIT_MESSAGE"
if [ $? -ne 0 ]; then
  echo "Error: Failed to commit changes."
  exit 1
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push origin $CURRENT_BRANCH
if [ $? -ne 0 ]; then
  echo "Error: Failed to push to GitHub."
  echo "Check your internet connection and GitHub access."
  exit 1
fi

# Generate pull request URL
REPO_URL=$(git config --get remote.origin.url)
REPO_URL=${REPO_URL%.git}
if [[ $REPO_URL == *"github.com"* ]]; then
  PR_URL="$REPO_URL/pull/new/$CURRENT_BRANCH"
  echo ""
  echo "Success! Your changes have been pushed to GitHub."
  echo ""
  echo "Opening pull request page in your browser..."
  if command -v xdg-open &> /dev/null; then
    xdg-open "$PR_URL"
  elif command -v open &> /dev/null; then
    open "$PR_URL"
  elif command -v start &> /dev/null; then
    start "$PR_URL"
  else
    echo "Could not open browser automatically."
    echo "Please open this URL to create a pull request:"
    echo "$PR_URL"
  fi
else
  echo ""
  echo "Success! Your changes have been pushed to the remote repository."
  echo ""
  echo "Please create a pull request through your repository's web interface."
fi

echo ""
echo "Next steps:"
echo "1. Complete the pull request form on GitHub"
echo "2. Wait for review or merge the pull request yourself"
echo "3. After merging, you can delete the branch if no longer needed"

exit 0
