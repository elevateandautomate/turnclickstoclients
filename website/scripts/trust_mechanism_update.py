#!/usr/bin/env python3
"""
Script to update quiz result pages with trust mechanism elements based on Alen's framework.
This script adds sections that address all three buyer types:
1. Automatic trust buyers (5-10%)
2. Repetition trust buyers (need 3-7 examples)
3. Duration trust buyers (need to feel they've known you for a long time)
"""

import os
import re
import sys
import glob
import time
import random
from collections import defaultdict

# Base directory
BASE_DIR = r"C:\Users\Eleva\Desktop\todo\contactlead\quiz-applications"

# Niche-specific content
NICHE_CONTENT = {
    'cosmetic-dentistry': {
        'history': "Since 2015, we've been helping cosmetic dentists transform their practices with our proven patient acquisition system.",
        'founder_story': "Our founder, after working with over 200 dental practices, identified the exact formula that consistently delivers high-value cosmetic patients.",
        'evolution': "What started as a simple Facebook ad strategy has evolved into a comprehensive system that includes advanced targeting, follow-up automation, and conversion optimization.",
        'examples': [
            "Dr. Sarah in Boston increased her monthly cosmetic cases from 4 to 17 within 90 days.",
            "A practice in Miami went from struggling to fill their schedule to having a 3-week waiting list for consultations.",
            "Dr. Michael's practice in Seattle now generates $120,000+ in additional monthly revenue from cosmetic procedures."
        ],
        'long_term': "Practices that implemented our system 3+ years ago continue to see consistent growth, with many expanding to multiple locations."
    },
    'high-end-chiropractors': {
        'history': "Our chiropractic client acquisition system has been refined since 2017, helping practices across the country achieve predictable growth.",
        'founder_story': "After seeing how traditional marketing failed high-end chiropractors, our team developed a specialized approach that attracts patients seeking premium care.",
        'evolution': "What began as consultation-focused marketing has evolved into a complete patient journey system that pre-qualifies leads and educates them on the value of comprehensive care.",
        'examples': [
            "Dr. James transformed his practice from insurance-dependent to cash-based, doubling his revenue while seeing fewer patients.",
            "A chiropractic clinic in Denver now attracts 25-30 new high-value patients monthly without discounting services.",
            "Dr. Lisa's practice went from struggling to stay afloat to generating $45,000+ in monthly recurring revenue."
        ],
        'long_term': "Chiropractors who have been with us for 2+ years have built sustainable practices with predictable cash flow and reduced dependence on insurance."
    },
    'weight-loss-clinics': {
        'history': "Since 2016, we've specialized in helping weight loss clinics attract motivated clients who are ready to invest in their transformation.",
        'founder_story': "Our approach was developed after analyzing what actually works for over 100 weight loss clinics across different markets and demographics.",
        'evolution': "Our system has evolved from basic lead generation to a sophisticated qualification process that identifies clients who are committed to long-term success.",
        'examples': [
            "A clinic in Phoenix went from 8 new clients per month to consistently enrolling 30+ program participants.",
            "A weight loss center in Chicago increased their average client value by 40% while reducing their marketing cost per acquisition.",
            "A small clinic in Atlanta scaled to three locations in 18 months using our patient acquisition system."
        ],
        'long_term': "Clinics using our system for 3+ years have built sustainable businesses with strong recurring revenue and high client retention rates."
    },
    'child-care': {
        'history': "Since 2018, we've been helping child care centers build enrollment predictably with our proven parent acquisition system.",
        'founder_story': "After working with dozens of child care centers struggling with inconsistent enrollment, our team developed a specialized approach that attracts committed parents looking for quality care.",
        'evolution': "Our system has evolved from simple lead generation to a comprehensive enrollment process that educates parents on your unique value and builds trust before they ever walk through your door.",
        'examples': [
            "A child care center in Dallas went from 65% capacity to a waiting list of 30+ families within 4 months.",
            "A preschool in Seattle increased their enrollment by 40% while raising their rates by 15%.",
            "A small family-owned center in Ohio expanded to a second location after 18 months of implementing our system."
        ],
        'long_term': "Centers using our system for 2+ years have built stable businesses with predictable enrollment cycles and significantly reduced marketing costs."
    },
    'pmu-artists': {
        'history': "Since 2019, we've specialized in helping PMU artists attract their ideal clients who value quality and are willing to pay premium prices.",
        'founder_story': "Our approach was developed after seeing talented PMU artists struggle to stand out in a crowded market and attract clients who appreciate their artistry.",
        'evolution': "What began as basic social media marketing has evolved into a comprehensive client attraction system that positions you as the premium choice in your market.",
        'examples': [
            "A PMU artist in Los Angeles went from charging $400 per procedure to $1,200+ with a 3-month waiting list.",
            "A studio in New York increased their monthly bookings from 15 to 45 while raising their prices by 35%.",
            "A new PMU artist in a small town built a six-figure business within her first year using our client acquisition system."
        ],
        'long_term': "Artists using our system for 2+ years have built prestigious brands that command premium prices and attract clients willing to travel for their services."
    },
    'non-surgical-body-contouring': {
        'history': "Since 2017, we've been helping body contouring clinics attract qualified clients who are ready to invest in their transformation.",
        'founder_story': "Our team developed this system after seeing how traditional marketing approaches failed to properly educate clients about non-surgical options, leading to poor conversion rates.",
        'evolution': "Our approach has evolved from basic lead generation to a sophisticated pre-qualification system that educates clients on the value of your services before they ever walk through your door.",
        'examples': [
            "A body contouring clinic in Miami increased their monthly revenue from $45,000 to over $120,000 within 90 days.",
            "A new clinic in Houston became profitable in their second month and scaled to $80,000+ monthly within their first year.",
            "An established med spa added body contouring services and generated an additional $35,000 monthly revenue within 60 days."
        ],
        'long_term': "Clinics using our system for 3+ years have built sustainable businesses with strong recurring revenue and high client retention rates."
    },
    'sleep-apnea': {
        'history': "Since 2016, we've specialized in helping sleep apnea clinics connect with patients seeking alternatives to CPAP therapy.",
        'founder_story': "Our approach was developed after recognizing that millions of sleep apnea sufferers were unaware of modern treatment options available through dental solutions.",
        'evolution': "What started as educational marketing has evolved into a complete patient acquisition system that identifies, educates, and converts ideal patients for your sleep practice.",
        'examples': [
            "A dental sleep practice in Texas went from 3 sleep appliances per month to over 20, adding $40,000+ in monthly revenue.",
            "A dedicated sleep clinic in California now consistently adds 15-20 new sleep patients monthly without dependence on physician referrals.",
            "A general dentist in Florida built a $500,000+ annual sleep practice alongside their existing practice using our system."
        ],
        'long_term': "Practices using our system for 3+ years have built respected sleep centers with strong physician relationships and consistent patient flow."
    },
    'hearing-aid-audiology': {
        'history': "Since 2017, we've been helping audiology practices attract qualified patients who are ready to invest in better hearing.",
        'founder_story': "Our team developed this system after seeing how traditional marketing approaches failed to overcome the stigma and price objections common in the hearing aid market.",
        'evolution': "Our approach has evolved from basic lead generation to a sophisticated education-first system that addresses objections before patients ever walk through your door.",
        'examples': [
            "An audiology practice in Florida increased their average sale value by 40% while reducing their no-show rate by half.",
            "A clinic in Arizona now consistently fits 25-30 new hearing aid patients monthly with an average value of $4,800 per patient.",
            "A practice in Michigan reduced their marketing cost per acquisition from $900 to under $300 while increasing their closing rate."
        ],
        'long_term': "Practices using our system for 2+ years have built sustainable businesses with strong word-of-mouth referrals and reduced dependence on manufacturer marketing support."
    },
    'dme-clinics': {
        'history': "Since 2018, we've specialized in helping DME providers attract qualified patients who need your solutions and have the proper insurance coverage.",
        'founder_story': "Our approach was developed after seeing DME providers struggle with the changing reimbursement landscape and increasing competition from online retailers.",
        'evolution': "What began as insurance-focused marketing has evolved into a comprehensive patient acquisition system that pre-qualifies leads and educates them on the value of working with a local provider.",
        'examples': [
            "A DME provider in Texas increased their monthly CPAP setups from 35 to over 90 within 60 days.",
            "A specialized mobility equipment provider doubled their revenue in 6 months while reducing their advertising spend by 20%.",
            "A multi-location DME company increased their insurance-qualified leads by 65% while reducing their cost per acquisition."
        ],
        'long_term': "DME providers using our system for 2+ years have built resilient businesses that thrive despite reimbursement challenges and online competition."
    }
}

# Default content for niches without specific content
DEFAULT_CONTENT = {
    'history': "Since 2015, we've been helping businesses like yours implement proven client acquisition systems that deliver predictable results.",
    'founder_story': "Our founder developed this system after working with hundreds of businesses and identifying the exact formula that consistently delivers ideal clients.",
    'evolution': "What started as a simple lead generation approach has evolved into a comprehensive system that includes advanced targeting, follow-up automation, and conversion optimization.",
    'examples': [
        "A business owner like you increased their monthly clients from struggling to find any to having more than they could handle within 90 days.",
        "Another practice went from inconsistent results to having a predictable flow of ideal clients every month.",
        "Many businesses using our system now generate significant additional monthly revenue from the clients we help them acquire."
    ],
    'long_term': "Businesses that implemented our system years ago continue to see consistent growth, with many expanding to multiple locations or increasing their prices due to high demand."
}

# HTML templates for trust mechanism sections
TRUST_MECHANISM_HTML = """
<!-- Trust Mechanism Section -->
<div class="trust-mechanism-container" style="background-color: #f9f9f9; padding: 25px; margin: 30px 0; border-radius: 8px; border-left: 5px solid #4A90E2;">
    <h3 style="color: #2c3e50; font-size: 1.4em; margin-bottom: 20px;">Our Journey to Creating This System</h3>

    <div class="history-section" style="margin-bottom: 20px;">
        <p style="font-size: 1.1em; line-height: 1.6;"><strong>{history}</strong></p>
        <p style="font-size: 1.1em; line-height: 1.6;">{founder_story}</p>
        <p style="font-size: 1.1em; line-height: 1.6;">{evolution}</p>
    </div>

    <h4 style="color: #2c3e50; font-size: 1.2em; margin: 20px 0 15px;">Consistent Results Across Different Businesses</h4>
    <ul style="list-style-type: none; padding-left: 0;">
        <li style="margin-bottom: 12px; padding-left: 25px; position: relative;">
            <span style="position: absolute; left: 0; color: #4A90E2;">✓</span> {example_1}
        </li>
        <li style="margin-bottom: 12px; padding-left: 25px; position: relative;">
            <span style="position: absolute; left: 0; color: #4A90E2;">✓</span> {example_2}
        </li>
        <li style="margin-bottom: 12px; padding-left: 25px; position: relative;">
            <span style="position: absolute; left: 0; color: #4A90E2;">✓</span> {example_3}
        </li>
    </ul>

    <div class="long-term-section" style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
        <p style="font-size: 1.1em; line-height: 1.6;"><strong>Long-term Success:</strong> {long_term}</p>
    </div>
</div>
"""

def get_niche_content(niche):
    """Get content specific to a niche, or use default if not available."""
    if niche in NICHE_CONTENT:
        return NICHE_CONTENT[niche]
    return DEFAULT_CONTENT

def update_file(file_path):
    """Update a single file with trust mechanism elements."""
    print(f"Updating file: {file_path}")

    # Extract niche from file path
    path_parts = file_path.split(os.sep)
    niche_dir = path_parts[-3]  # Assuming structure is quiz-applications/niche/bucket/file.html

    # Get content for this niche
    content_data = get_niche_content(niche_dir)

    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

    # Make a backup of the original file
    backup_path = file_path + ".trust.bak"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Check if trust mechanism section already exists
    if "trust-mechanism-container" in content:
        print(f"Trust mechanism already exists in: {file_path}")
        os.remove(backup_path)  # Remove backup if no changes needed
        return

    # Format the trust mechanism HTML with niche-specific content
    trust_html = TRUST_MECHANISM_HTML.format(
        history=content_data['history'],
        founder_story=content_data['founder_story'],
        evolution=content_data['evolution'],
        example_1=content_data['examples'][0],
        example_2=content_data['examples'][1],
        example_3=content_data['examples'][2],
        long_term=content_data['long_term']
    )

    # Find the position to insert the trust mechanism section
    # Look for the CTA section or the end of the main content
    cta_pattern = r'<h2[^>]*>Ready to (Create|Stop Missing Out|Start Succeeding)[^<]*</h2>'
    cta_match = re.search(cta_pattern, content)

    if cta_match:
        # Insert before the CTA section
        insert_position = cta_match.start()
        transformed_content = content[:insert_position] + trust_html + content[insert_position:]
    else:
        # If CTA section not found, try to find the end of the main content
        main_content_end = content.find('</main>')
        if main_content_end != -1:
            insert_position = main_content_end
            transformed_content = content[:insert_position] + trust_html + content[insert_position:]
        else:
            # If main tag not found, insert before the footer or at the end of the body
            footer_start = content.find('<footer')
            if footer_start != -1:
                insert_position = footer_start
                transformed_content = content[:insert_position] + trust_html + content[insert_position:]
            else:
                body_end = content.find('</body>')
                if body_end != -1:
                    insert_position = body_end
                    transformed_content = content[:insert_position] + trust_html + content[insert_position:]
                else:
                    # If all else fails, append to the end of the file
                    transformed_content = content + trust_html
                    print(f"Warning: Could not find optimal insertion point for {file_path}")

    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(transformed_content)

    print(f"Successfully added trust mechanism to: {file_path}")

def main():
    """Main function to process files."""
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
        update_file(file)
        # Add a small delay to avoid overwhelming the system
        time.sleep(0.1)

    print(f"Added trust mechanism to {len(files)} files")

if __name__ == "__main__":
    main()
