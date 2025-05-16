#!/usr/bin/env python3
"""
Script to generate missing results pages.
This script will:
1. Find all missing results pages
2. Create them based on existing templates
"""

import os
import shutil
import re
import glob
from pathlib import Path

# Path to the quiz applications directory
QUIZ_APPLICATIONS_DIR = 'quiz-applications'

# Niches
NICHES = [
    'cosmetic-dentistry',
    'child-care-centers',
    'pmu-artists',
    'sleep-apnea-snoring-clinics',
    'hearing-aid-audiology-clinics',
    'dme-clinics',
    'non-surgical-body-contouring'
]

# Buckets
BUCKETS = [
    # These buckets are already working
    # 'foundation',
    # 'growth',
    # 'scaling',
    # 'operations',
    # 'referrals',

    # These buckets are still missing
    'clients',
    'patients',
    'practice',
    'enrollment',
    'future',
    'studio'
]

# Variants
VARIANTS = [
    'a-solution',
    'b-problem',
    'c-most-aware'
]

def find_template_pages():
    """Find template pages to use for creating missing pages."""
    templates = {}

    # Define source buckets to use as templates for missing buckets
    source_buckets = {
        'clients': 'foundation',
        'patients': 'foundation',
        'practice': 'foundation',
        'enrollment': 'growth',
        'future': 'growth',
        'studio': 'scaling'
    }

    # Look for existing pages to use as templates
    for niche in NICHES:
        templates[niche] = {}
        for bucket in BUCKETS:
            templates[niche][bucket] = {}

            # Try to find existing templates first
            for variant in VARIANTS:
                page_path = os.path.join(QUIZ_APPLICATIONS_DIR, niche, bucket, f"{bucket}-variant-{variant}.html")
                if os.path.exists(page_path):
                    templates[niche][bucket][variant] = page_path

            # If no templates found, use source buckets
            if not any(templates[niche][bucket].values()):
                source_bucket = source_buckets.get(bucket)
                if source_bucket:
                    for variant in VARIANTS:
                        source_path = os.path.join(QUIZ_APPLICATIONS_DIR, niche, source_bucket, f"{source_bucket}-variant-{variant}.html")
                        if os.path.exists(source_path):
                            templates[niche][bucket][variant] = source_path

    # If a niche doesn't have any templates, use templates from another niche
    for niche in NICHES:
        for bucket in BUCKETS:
            if not templates[niche].get(bucket):
                templates[niche][bucket] = {}

            for variant in VARIANTS:
                if not templates[niche][bucket].get(variant):
                    # Look for a template in another niche
                    for other_niche in NICHES:
                        if other_niche != niche:
                            # First try the same bucket in another niche
                            template_path = os.path.join(QUIZ_APPLICATIONS_DIR, other_niche, bucket, f"{bucket}-variant-{variant}.html")
                            if os.path.exists(template_path):
                                templates[niche][bucket][variant] = template_path
                                break

                            # If not found, try the source bucket in another niche
                            source_bucket = source_buckets.get(bucket)
                            if source_bucket:
                                template_path = os.path.join(QUIZ_APPLICATIONS_DIR, other_niche, source_bucket, f"{source_bucket}-variant-{variant}.html")
                                if os.path.exists(template_path):
                                    templates[niche][bucket][variant] = template_path
                                    break

    return templates

def create_missing_pages(templates):
    """Create missing results pages based on templates."""
    created_count = 0

    for niche in NICHES:
        for bucket in BUCKETS:
            # Create the bucket directory if it doesn't exist
            bucket_dir = os.path.join(QUIZ_APPLICATIONS_DIR, niche, bucket)
            os.makedirs(bucket_dir, exist_ok=True)

            for variant in VARIANTS:
                page_path = os.path.join(bucket_dir, f"{bucket}-variant-{variant}.html")

                # Skip if the page already exists
                if os.path.exists(page_path):
                    continue

                # Find a template to use
                template_path = templates[niche][bucket].get(variant)
                if not template_path:
                    # If no template for this variant, use a template from another variant
                    for other_variant in VARIANTS:
                        if other_variant != variant:
                            template_path = templates[niche][bucket].get(other_variant)
                            if template_path:
                                break

                if template_path:
                    # Create the page based on the template
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Get template details
                    template_parts = template_path.split(os.sep)
                    template_niche = template_parts[1]
                    template_bucket = template_parts[2]
                    template_file = template_parts[3]
                    template_variant = template_file.split('-variant-')[1].split('.')[0]

                    # Replace the file name in the content (e.g., foundation-variant-a-solution.html -> clients-variant-a-solution.html)
                    content = content.replace(f"{template_bucket}-variant-{template_variant}", f"{bucket}-variant-{variant}")

                    # Replace title and headings
                    content = content.replace(f"{template_bucket.capitalize()} {template_variant.replace('-', ' ').title()}",
                                             f"{bucket.capitalize()} {variant.replace('-', ' ').title()}")

                    # Replace any URLs or paths
                    content = content.replace(f"/{template_niche}/", f"/{niche}/")
                    content = content.replace(f"/{template_bucket}/", f"/{bucket}/")

                    # Replace any specific content related to the bucket
                    bucket_terms = {
                        'foundation': ['foundation', 'foundations', 'basic', 'basics', 'fundamental', 'fundamentals', 'starting', 'start'],
                        'growth': ['growth', 'growing', 'expand', 'expansion', 'scaling up', 'increase'],
                        'scaling': ['scaling', 'scale', 'expansion', 'growing rapidly', 'accelerate'],
                        'clients': ['clients', 'client', 'customer', 'customers', 'clientele'],
                        'patients': ['patients', 'patient', 'care', 'healthcare', 'medical'],
                        'practice': ['practice', 'business', 'office', 'clinic', 'operation'],
                        'operations': ['operations', 'processes', 'workflow', 'efficiency', 'systems'],
                        'enrollment': ['enrollment', 'sign up', 'registration', 'onboarding', 'joining'],
                        'future': ['future', 'planning', 'long-term', 'vision', 'strategy'],
                        'studio': ['studio', 'workspace', 'office', 'environment', 'facility'],
                        'referrals': ['referrals', 'referral', 'recommendation', 'word of mouth', 'refer']
                    }

                    # Replace bucket-specific terms
                    if template_bucket in bucket_terms and bucket in bucket_terms:
                        for template_term in bucket_terms[template_bucket]:
                            for bucket_term in bucket_terms[bucket]:
                                content = content.replace(f" {template_term} ", f" {bucket_term} ")
                                content = content.replace(f"{template_term.capitalize()} ", f"{bucket_term.capitalize()} ")

                    # Write the new page
                    with open(page_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print(f"Created {page_path}")
                    created_count += 1

                    # Create split test variations
                    for split in range(1, 4):
                        split_path = os.path.join(bucket_dir, f"{bucket}-variant-{variant}-split{split}.html")
                        if not os.path.exists(split_path):
                            # Create the split test variation
                            with open(split_path, 'w', encoding='utf-8') as f:
                                # Add a comment to indicate this is a split test variation
                                split_content = content.replace('</head>', f'<!-- Split Test Variation {split} --></head>')
                                # Add a visual indicator for testing
                                split_content = split_content.replace('<body', f'<body data-split="{split}"')
                                # Add split-specific content
                                split_content = split_content.replace('<h1>', f'<h1>Split {split}: ')
                                f.write(split_content)

                            print(f"Created {split_path}")
                            created_count += 1

    return created_count

def main():
    """Main function."""
    print("Finding template pages...")
    templates = find_template_pages()

    print("Creating missing pages...")
    created_count = create_missing_pages(templates)

    print(f"\nCreated {created_count} missing pages")

if __name__ == "__main__":
    main()
