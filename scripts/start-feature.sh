#!/bin/bash

# Script to start a new feature branch for website updates

# Display help if no arguments or help flag
if [ "$1" == "" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  echo "Usage: ./scripts/start-feature.sh <branch-name>"
  echo ""
  echo "Examples:"
  echo "  ./scripts/start-feature.sh feature-newsletter-signup"
  echo "  ./scripts/start-feature.sh fix-mobile-navigation"
  echo "  ./scripts/start-feature.sh update-pricing-page"
  echo ""
  echo "Branch naming conventions:"
  echo "  feature-* for new features"
  echo "  fix-* for bug fixes"
  echo "  update-* for content updates"
  echo "  improve-* for improvements to existing features"
  exit 0
fi

# Get branch name from argument
BRANCH_NAME=$1

# Check if branch name follows conventions
if [[ ! $BRANCH_NAME =~ ^(feature|fix|update|improve)- ]]; then
  echo "Warning: Branch name doesn't follow naming conventions."
  echo "Recommended prefixes: feature-, fix-, update-, improve-"
  echo ""
  read -p "Continue with this branch name anyway? (y/n): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then
    echo "Aborting. Please restart with a proper branch name."
    exit 1
  fi
fi

# Make sure we have the latest main
echo "Updating main branch..."
git checkout main
if [ $? -ne 0 ]; then
  echo "Error: Failed to checkout main branch."
  echo "Make sure you have a clean working directory and try again."
  exit 1
fi

git pull
if [ $? -ne 0 ]; then
  echo "Error: Failed to pull latest changes from main."
  echo "Check your internet connection and GitHub access."
  exit 1
fi

# Create and checkout new branch
echo "Creating new branch: $BRANCH_NAME"
git checkout -b $BRANCH_NAME
if [ $? -ne 0 ]; then
  echo "Error: Failed to create new branch."
  echo "The branch might already exist or there might be conflicts."
  exit 1
fi

# Success message
echo ""
echo "Success! You're now on branch: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "1. Make your changes to the website"
echo "2. Test your changes thoroughly"
echo "3. Run ./scripts/prepare-pr.sh when ready to submit a pull request"
echo ""
echo "Current branch status:"
git status

exit 0
