#!/usr/bin/env python3
"""
Script to update quiz result pages with belief shifting framework templates.
This script will insert the appropriate templates based on the niche and page type.
"""

import os
import re
import sys
import glob

# Base directory
BASE_DIR = r"C:\Users\Eleva\Desktop\todo\contactlead\quiz-applications"

# Template file
TEMPLATE_FILE = r"C:\Users\Eleva\Desktop\todo\contactlead\scripts\belief-shifting-templates.md"

# Load templates
def load_templates():
    """Load templates from the template file."""
    templates = {}

    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

            # Split by niche sections
            niche_sections = re.split(r'## (.+) Template', content)[1:]  # Skip the first empty part

            # Process each niche and its sections
            for i in range(0, len(niche_sections), 2):
                if i+1 >= len(niche_sections):
                    break

                niche_name = niche_sections[i].lower().replace(' ', '-')
                niche_content = niche_sections[i+1]

                # Initialize niche in templates
                templates[niche_name] = {}

                # Split by section headers
                section_parts = re.split(r'### (.+) Section', niche_content)[1:]  # Skip the first empty part

                # Process each section
                for j in range(0, len(section_parts), 2):
                    if j+1 >= len(section_parts):
                        break

                    section_name = section_parts[j].lower().replace(' ', '-')
                    section_content = section_parts[j+1]

                    # Extract HTML content between ```html and ```
                    html_match = re.search(r'```html\s*(.*?)\s*```', section_content, re.DOTALL)
                    if html_match:
                        templates[niche_name][section_name] = html_match.group(1)

        # Print available templates for debugging
        print(f"Loaded templates for niches: {list(templates.keys())}")
        for niche in templates:
            print(f"  {niche} sections: {list(templates[niche].keys())}")

        return templates

    except Exception as e:
        print(f"Error loading templates: {e}")
        # Return empty templates as fallback
        return {
            "cosmetic-dentistry": {
                "what's-possible": "<div>Fallback template</div>",
                "gap": "<div>Fallback template</div>",
                "cta-enhancement": "<div>Fallback template</div>"
            }
        }

# Map directory names to template keys
NICHE_MAP = {
    'cosmetic-dentistry': 'cosmetic-dentistry',
    'child-care': 'child-care-centers',
    'pmu-artists': 'pmu-artists',
    'weight-loss-clinics': 'weight-loss-clinics',
    'high-end-chiropractors': 'high-end-chiropractors',
    'non-surgical-body-contouring': 'non-surgical-body-contouring',
    'sleep-apnea': 'sleep-apnea',
    'hearing-aid-audiology': 'hearing-aid-audiology',
    'dme-clinics': 'dme-clinics'
}

def update_file(file_path, templates):
    """Update a single file with the appropriate templates."""
    print(f"Updating file: {file_path}")

    # Extract niche from file path
    path_parts = file_path.split(os.sep)
    niche_dir = path_parts[-3]  # Assuming structure is quiz-applications/niche/bucket/file.html
    bucket_dir = path_parts[-2]  # Get the bucket (foundation, growth, scaling, etc.)

    # Extract variant from filename (a-solution, b-problem, c-most-aware)
    filename = os.path.basename(file_path)
    variant_match = re.search(r'variant-([abc]-\w+)', filename)
    variant = variant_match.group(1) if variant_match else "unknown"

    print(f"Processing niche: {niche_dir}, bucket: {bucket_dir}, variant: {variant}")

    # Map directory name to template key
    template_key = NICHE_MAP.get(niche_dir, niche_dir)

    # If we don't have templates for this niche, use a default
    if template_key not in templates:
        print(f"No templates found for niche: {niche_dir}, using cosmetic-dentistry as default")
        template_key = 'cosmetic-dentistry'

    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

    # Check if the file already has our belief shifting sections
    if "What's Possible (That You're Missing Out On)" in content:
        print(f"File already has belief shifting framework: {file_path}")

        # Clean up any duplicate sections that might have been added
        # This is a more aggressive approach to fix files that might have been corrupted
        if content.count("What's Possible (That You're Missing Out On)") > 1:
            print(f"Fixing duplicate belief shifting sections in: {file_path}")

            # Find all occurrences of the belief shifting sections
            possible_sections = re.findall(r'<div style="background-color: #f9f9f9; padding: 30px; border-radius: 8px; margin: 30px 0; border-left: 5px solid #0077b6;">.*?</div>\s*<div style="background-color: #FFF8E1; padding: 30px; border-radius: 8px; margin: 30px 0; border: 1px solid #FFB74D;">.*?</div>', content, re.DOTALL)

            if len(possible_sections) > 1:
                # Keep only the first occurrence and remove others
                for section in possible_sections[1:]:
                    content = content.replace(section, '')

                # Write the cleaned content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Removed {len(possible_sections)-1} duplicate belief shifting sections")

        return

    # Make a backup of the original file
    backup_path = file_path + ".bak"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Get templates for this niche
    try:
        whats_possible_template = templates[template_key]["what's-possible"]
    except KeyError:
        # Try alternative key names
        if "whats-possible" in templates[template_key]:
            whats_possible_template = templates[template_key]["whats-possible"]
        else:
            print(f"Available keys in template: {list(templates[template_key].keys())}")
            # Default to cosmetic dentistry template
            whats_possible_template = templates["cosmetic-dentistry"]["what's-possible"]

    try:
        gap_template = templates[template_key]["gap"]
    except KeyError:
        # Default to cosmetic dentistry template
        gap_template = templates["cosmetic-dentistry"]["gap"]

    # For CTA enhancement, we need to handle different possible key names
    cta_key_options = ["cta-enhancement", "cta", "cta enhancement"]
    cta_template = None

    # Try to find a matching key in the current niche template
    for key in cta_key_options:
        if key in templates[template_key]:
            cta_template = templates[template_key][key]
            break

    # If not found, try cosmetic dentistry template
    if cta_template is None:
        for key in cta_key_options:
            if key in templates["cosmetic-dentistry"]:
                cta_template = templates["cosmetic-dentistry"][key]
                break

    # If still not found, use a simple default template
    if cta_template is None:
        print("Using default CTA template")
        cta_template = """
        <div style="background: rgba(255,255,255,0.15); padding: 25px; border-radius: 8px; margin: 25px 0; text-align: left; border-left: 4px solid #FFC107;">
            <h3 style="color: #ffffff; margin-top: 0; margin-bottom: 15px;">What You're Currently Missing Out On:</h3>
            <ul style="text-align: left; padding-left: 20px; margin-bottom: 0;">
                <li style="margin-bottom: 15px;"><strong>The Proven System:</strong> While you're struggling, others are leveraging a system that automatically brings ideal clients to their door.</li>
                <li style="margin-bottom: 15px;"><strong>The Financial Security:</strong> As you worry about inconsistent revenue, others with this system enjoy predictable, growing income month after month.</li>
                <li style="margin-bottom: 0;"><strong>The Peace of Mind:</strong> Rather than stressing about marketing, these professionals sleep well knowing their client pipeline is consistently full.</li>
            </ul>
        </div>

        <p style="font-size: 1.2em; font-weight: bold; margin: 25px 0;">Every day you wait is another day of missed opportunities and falling further behind those who have already implemented this system.</p>
        """

    # Customize templates based on variant
    if 'a-solution' in variant:
        # Solution-aware customization
        whats_possible_template = whats_possible_template.replace(
            "What's Possible (That You're Missing Out On)",
            "What's Possible With This Solution (That You're Missing Out On)"
        )
    elif 'b-problem' in variant:
        # Problem-aware customization
        whats_possible_template = whats_possible_template.replace(
            "What's Possible (That You're Missing Out On)",
            "What's Possible When You Solve This Problem (That You're Missing Out On)"
        )

    # Different insertion strategies based on page structure
    modified = False

    # First, check if the file has a main content section
    main_content_patterns = [
        r'(<div class="solution-content-section">.*?)(</div>\s*</div>)',
        r'(<div class="content-section">.*?)(</div>\s*</div>)',
        r'(<div class="main-content">.*?)(</div>\s*</div>)',
        r'(<main.*?>.*?)(</main>)',
        r'(<div class="premium-container">.*?)(</div>\s*</div>)'
    ]

    for pattern in main_content_patterns:
        if re.search(pattern, content, re.DOTALL):
            # Insert before the end of the main content section
            content = re.sub(
                pattern,
                r'\1\n\n' + whats_possible_template + '\n\n' + gap_template + r'\2',
                content,
                count=1,
                flags=re.DOTALL
            )
            modified = True
            break

    # Strategy 1: If no main content section found, look for a section after problem description
    if not modified:
        problem_section_patterns = [
            r'(<div class="section consequences">.*?</div>)',
            r'(<div class="section problem-agitation">.*?</div>)',
            r'(<div class="problem-section">.*?</div>)',
            r'(<div class="pain-points">.*?</div>)',
            r'(<ul class="problem-list">.*?</ul>)',
            r'(<div class="how-it-works-section">.*?</div>)',
            r'(<div class="benefits-list">.*?</div>)'
        ]

        for pattern in problem_section_patterns:
            if re.search(pattern, content, re.DOTALL):
                # Insert after problem section
                content = re.sub(
                    pattern,
                    r'\1\n\n' + whats_possible_template + '\n\n' + gap_template,
                    content,
                    count=1,
                    flags=re.DOTALL
                )
                modified = True
                break

    # Strategy 2: If still not found, insert after introduction paragraph
    if not modified:
        intro_patterns = [
            r'(<p class="subtitle">.*?</p>\s*<p>.*?</p>)',
            r'(<p style="text-align:center;.*?</p>\s*<p>.*?</p>)',
            r'(<p>.*?</p>\s*<p>.*?</p>)',
            r'(<h3>.*?</h3>\s*<p>.*?</p>)'
        ]

        for pattern in intro_patterns:
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(
                    pattern,
                    r'\1\n\n' + whats_possible_template + '\n\n' + gap_template,
                    content,
                    count=1,
                    flags=re.DOTALL
                )
                modified = True
                break

    # Update CTA section
    cta_patterns = [
        r'(<div class="cta-section">.*?)(</div>\s*</div>)',
        r'(<div class="final-cta-section">.*?)(</div>\s*</div>)',
        r'(<div class="action-section">.*?)(</div>\s*</div>)',
        r'(<div class="next-step-cta">.*?)(</div>)'
    ]

    cta_modified = False
    for pattern in cta_patterns:
        if re.search(pattern, content, re.DOTALL):
            # Find the heading in the CTA section
            cta_section = re.search(pattern, content, re.DOTALL).group(1)

            # Check if there's a heading we can replace
            heading_match = re.search(r'(<h[23].*?>)(.*?)(</h[23]>)', cta_section, re.DOTALL)
            if heading_match:
                # Replace the heading
                new_heading = heading_match.group(1) + "Ready to Stop Missing Out on the Success Other Professionals Are Already Enjoying?" + heading_match.group(3)
                modified_cta = cta_section.replace(heading_match.group(0), new_heading)

                # Find a good spot to insert our CTA content
                # Try to find a paragraph or button to insert before
                insert_point_match = re.search(r'(<p.*?>.*?</p>|<a.*?class="cta-button.*?</a>|<button.*?</button>)', modified_cta, re.DOTALL)
                if insert_point_match:
                    insert_point = insert_point_match.group(0)
                    modified_cta = modified_cta.replace(insert_point, cta_template + "\n\n" + insert_point)
                else:
                    # If no good insertion point, just append to the end
                    modified_cta += "\n\n" + cta_template

                # Replace the entire CTA section
                content = content.replace(cta_section, modified_cta)
                cta_modified = True
                break
            else:
                # If no heading found, just append our template to the CTA section
                content = re.sub(
                    pattern,
                    r'\1\n\n' + cta_template + r'\2',
                    content,
                    count=1,
                    flags=re.DOTALL
                )
                cta_modified = True
                break

    # Write the updated content back to the file
    if modified or cta_modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated: {file_path}")
    else:
        print(f"Could not find appropriate insertion points in: {file_path}")
        # Restore from backup
        os.replace(backup_path, file_path)

def main():
    """Main function to process files."""
    # Load templates
    templates = load_templates()

    # Check command line arguments
    if len(sys.argv) > 1:
        niche = sys.argv[1]
        bucket = sys.argv[2] if len(sys.argv) > 2 else '*'
        variant = sys.argv[3] if len(sys.argv) > 3 else '*'

        # Process specific files
        pattern = os.path.join(BASE_DIR, niche, bucket, f"*{variant}*.html")
        files = glob.glob(pattern)
    else:
        # Process all files
        files = glob.glob(os.path.join(BASE_DIR, '*', '*', '*.html'))

    # Update each file
    for file in files:
        update_file(file, templates)

    print(f"Updated {len(files)} files")

if __name__ == "__main__":
    main()
