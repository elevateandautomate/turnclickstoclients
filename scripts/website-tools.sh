#!/bin/bash

# Website maintenance tools script

# Display help
show_help() {
  echo "TurnClicksToClients Website Tools"
  echo "================================="
  echo ""
  echo "Usage: ./scripts/website-tools.sh [command]"
  echo ""
  echo "Commands:"
  echo "  status              Show current git status and branch"
  echo "  branches            List all branches"
  echo "  update              Update main branch to latest version"
  echo "  check-html          Check HTML files for common issues"
  echo "  apply-to-all [cmd]  Apply a command to all HTML files"
  echo "  find-text [text]    Find text in all files"
  echo "  help                Show this help message"
  echo ""
  echo "Examples:"
  echo "  ./scripts/website-tools.sh status"
  echo "  ./scripts/website-tools.sh apply-to-all \"sed -i 's/old text/new text/g'\""
  echo "  ./scripts/website-tools.sh find-text \"text to find\""
  echo ""
}

# Check current status
show_status() {
  echo "Current Git Status:"
  echo "==================="
  git status
  
  echo ""
  echo "Current Branch:"
  echo "=============="
  git branch --show-current
  
  echo ""
  echo "Recent Commits:"
  echo "=============="
  git log --oneline -5
}

# List all branches
list_branches() {
  echo "Local Branches:"
  echo "=============="
  git branch
  
  echo ""
  echo "Remote Branches:"
  echo "==============="
  git branch -r
}

# Update main branch
update_main() {
  echo "Updating main branch..."
  
  # Store current branch
  CURRENT_BRANCH=$(git branch --show-current)
  
  # Check if working directory is clean
  if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory is not clean."
    echo "Please commit or stash your changes before updating."
    return 1
  fi
  
  # Switch to main and pull
  git checkout main
  git pull
  
  # Return to original branch if not on main
  if [ "$CURRENT_BRANCH" != "main" ]; then
    git checkout $CURRENT_BRANCH
    echo "Returned to branch: $CURRENT_BRANCH"
  fi
  
  echo "Main branch is now up to date."
}

# Check HTML files for common issues
check_html() {
  echo "Checking HTML files for common issues..."
  
  echo "1. Checking for broken HTML tags..."
  BROKEN_TAGS=$(grep -r --include="*.html" -l "<[a-z]\+[^>]*>[^<]*$" .)
  if [ -n "$BROKEN_TAGS" ]; then
    echo "Warning: Possible broken HTML tags found in:"
    echo "$BROKEN_TAGS"
  else
    echo "No broken HTML tags found."
  fi
  
  echo ""
  echo "2. Checking for missing alt attributes in images..."
  MISSING_ALT=$(grep -r --include="*.html" -l "<img[^>]*[^(alt=)][^>]*>" .)
  if [ -n "$MISSING_ALT" ]; then
    echo "Warning: Images without alt attributes found in:"
    echo "$MISSING_ALT"
  else
    echo "No images missing alt attributes found."
  fi
  
  echo ""
  echo "3. Checking for large HTML files (>100KB)..."
  find . -name "*.html" -type f -size +100k | grep -v "\.git/"
  
  echo ""
  echo "HTML check complete."
}

# Apply a command to all HTML files
apply_to_all() {
  if [ -z "$1" ]; then
    echo "Error: Command is required."
    echo "Usage: ./scripts/website-tools.sh apply-to-all \"command\""
    return 1
  fi
  
  COMMAND=$1
  echo "Applying command to all HTML files: $COMMAND"
  
  # Get count of HTML files
  HTML_COUNT=$(find . -name "*.html" -type f | grep -v "\.git/" | wc -l)
  echo "Found $HTML_COUNT HTML files."
  
  # Confirm before proceeding
  read -p "This will modify $HTML_COUNT files. Continue? (y/n): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then
    echo "Operation cancelled."
    return 1
  fi
  
  # Apply command to each file
  find . -name "*.html" -type f | grep -v "\.git/" | while read file; do
    echo "Processing: $file"
    eval "$COMMAND '$file'"
  done
  
  echo "Command applied to all HTML files."
}

# Find text in all files
find_text() {
  if [ -z "$1" ]; then
    echo "Error: Search text is required."
    echo "Usage: ./scripts/website-tools.sh find-text \"text to find\""
    return 1
  fi
  
  SEARCH_TEXT=$1
  echo "Searching for: \"$SEARCH_TEXT\""
  
  grep -r --include="*.html" --include="*.css" --include="*.js" "$SEARCH_TEXT" .
  
  echo "Search complete."
}

# Main script logic
case "$1" in
  status)
    show_status
    ;;
  branches)
    list_branches
    ;;
  update)
    update_main
    ;;
  check-html)
    check_html
    ;;
  apply-to-all)
    apply_to_all "$2"
    ;;
  find-text)
    find_text "$2"
    ;;
  help|--help|-h|"")
    show_help
    ;;
  *)
    echo "Unknown command: $1"
    echo "Run './scripts/website-tools.sh help' for usage information."
    exit 1
    ;;
esac

exit 0
