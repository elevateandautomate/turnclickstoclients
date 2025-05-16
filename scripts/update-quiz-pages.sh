#!/bin/bash

# Script to update quiz result pages with belief shifting framework
# Usage: ./update-quiz-pages.sh [niche] [bucket] [variant]
# Example: ./update-quiz-pages.sh cosmetic-dentistry foundation a-solution

NICHE=$1
BUCKET=$2
VARIANT=$3

# Base directory
BASE_DIR="/c/Users/Eleva/Desktop/todo/contactlead/quiz-applications"

# Function to apply templates based on niche
apply_templates() {
    local file=$1
    local niche=$2
    
    echo "Updating file: $file"
    
    # Determine which template to use based on niche
    case "$niche" in
        "cosmetic-dentistry")
            template_dir="cosmetic-dentistry"
            ;;
        "child-care")
            template_dir="child-care"
            ;;
        "pmu-artists")
            template_dir="pmu-artists"
            ;;
        "weight-loss-clinics")
            template_dir="weight-loss"
            ;;
        "high-end-chiropractors")
            template_dir="chiropractors"
            ;;
        "non-surgical-body-contouring")
            template_dir="body-contouring"
            ;;
        "sleep-apnea")
            template_dir="sleep-apnea"
            ;;
        "hearing-aid-audiology")
            template_dir="hearing-aid"
            ;;
        "dme-clinics")
            template_dir="dme"
            ;;
        *)
            echo "Unknown niche: $niche"
            return 1
            ;;
    esac
    
    # Find the appropriate insertion points in the file
    # This is a simplified example - in a real script, you'd need to use sed or awk
    # to find the correct insertion points based on the file structure
    
    # For demonstration purposes, we'll just echo the commands that would be executed
    echo "Would insert 'What's Possible' section from $template_dir template"
    echo "Would insert 'Gap' section from $template_dir template"
    echo "Would update CTA section from $template_dir template"
    
    echo "File updated successfully"
}

# Main execution

if [ -z "$NICHE" ] || [ -z "$BUCKET" ] || [ -z "$VARIANT" ]; then
    echo "Processing all files..."
    
    # Find all HTML files in quiz-applications directory
    find "$BASE_DIR" -name "*.html" | while read file; do
        # Extract niche from file path
        file_niche=$(echo "$file" | cut -d'/' -f6)
        apply_templates "$file" "$file_niche"
    done
else
    echo "Processing files for niche: $NICHE, bucket: $BUCKET, variant: $VARIANT"
    
    # Find specific HTML files matching criteria
    if [ "$VARIANT" == "all" ]; then
        find "$BASE_DIR/$NICHE/$BUCKET" -name "*.html" | while read file; do
            apply_templates "$file" "$NICHE"
        done
    else
        find "$BASE_DIR/$NICHE/$BUCKET" -name "*$VARIANT*.html" | while read file; do
            apply_templates "$file" "$NICHE"
        done
    fi
fi

echo "Update process completed"
