import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file before making changes"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def fix_c_most_aware_variant(quiz_file, content):
    """Fix variant inconsistency between c-most-aware and c-mostaware-long"""
    changes_made = False
    
    # Check if the quiz file uses c-most-aware but should use c-mostaware-long
    if 'awarenessVariant = "c-most-aware"' in content and 'c-mostaware-long' in content:
        # Replace in the assignment
        new_content = content.replace('awarenessVariant = "c-most-aware"', 'awarenessVariant = "c-mostaware-long"')
        
        # Replace in the URL construction if it's there
        new_content = new_content.replace('variant-${awarenessVariant}', 'variant-${awarenessVariant}')
        
        if new_content != content:
            changes_made = True
            content = new_content
            print(f"  Fixed c-most-aware to c-mostaware-long in {quiz_file}")
    
    return content, changes_made

def fix_url_construction(quiz_file, content, matching_dir):
    """Fix URL construction to match the directory structure"""
    changes_made = False
    
    # Find URL construction pattern
    url_pattern = r'const url = `(\.\.\/quiz-applications\/[^`]+)`'
    url_match = re.search(url_pattern, content)
    
    if url_match:
        current_url = url_match.group(1)
        
        # Check if URL uses the correct directory
        dir_pattern = r'\.\.\/quiz-applications\/([^/]+)\/'
        dir_match = re.search(dir_pattern, current_url)
        
        if dir_match and dir_match.group(1) != matching_dir:
            # Construct correct URL
            new_url = current_url.replace(dir_match.group(1), matching_dir)
            new_content = content.replace(current_url, new_url)
            
            if new_content != content:
                changes_made = True
                content = new_content
                print(f"  Fixed directory in URL: {dir_match.group(1)} -> {matching_dir} in {quiz_file}")
    
    return content, changes_made

def fix_filename_pattern(quiz_file, content, matching_dir, buckets, directory_info):
    """Fix filename pattern in URL to match actual files"""
    changes_made = False
    
    # Find URL construction pattern
    url_pattern = r'const url = `\.\.\/quiz-applications\/[^/]+\/\$\{scoreBucket\}\/([^`]+)`'
    url_match = re.search(url_pattern, content)
    
    if url_match:
        current_file_pattern = url_match.group(1)
        
        # Check if the pattern would match actual files
        sample_bucket = next(iter(buckets), None)
        if not sample_bucket:
            return content, changes_made
            
        sample_files = directory_info["buckets"][sample_bucket]["files"]
        if not sample_files:
            return content, changes_made
            
        # Get the first file to use as a reference
        sample_file = sample_files[0]
        
        # Extract the pattern from the actual file
        file_prefix = sample_file.split('variant-')[0]
        
        # Check if the URL pattern contains the correct file prefix
        if file_prefix and file_prefix not in current_file_pattern:
            # Construct correct pattern
            new_pattern = f"{file_prefix}variant-${{awarenessVariant}}.html${{baseParams && '?' + baseParams}}&bucket=${{scoreBucket}}&variant=${{awarenessVariant}}"
            
            # Replace in URL construction
            new_url = f"../quiz-applications/{matching_dir}/${{scoreBucket}}/{new_pattern}"
            current_url = f"../quiz-applications/{matching_dir}/${{scoreBucket}}/{current_file_pattern}"
            
            new_content = content.replace(
                f"const url = `{current_url}`",
                f"const url = `{new_url}`"
            )
            
            if new_content != content:
                changes_made = True
                content = new_content
                print(f"  Fixed filename pattern in URL in {quiz_file}")
    
    return content, changes_made

def fix_quiz_redirects():
    """Check and fix redirect issues in quiz HTML files"""
    quiz_applications_dir = 'quiz-applications'
    niches_dir = 'niches'
    
    # Special mappings for mismatched directory and quiz names
    special_mappings = {
        "cosmetic-dentists": "cosmetic-dentistry"
    }
    
    # Track issues and fixes
    issues_found = []
    fixes_made = []
    
    # Step 1: Get directory structure information
    print(f"Analyzing directory structure in {quiz_applications_dir}...")
    
    directories_info = {}
    quiz_dirs = [d for d in os.listdir(quiz_applications_dir) 
                if os.path.isdir(os.path.join(quiz_applications_dir, d))]
    
    for quiz_dir in quiz_dirs:
        quiz_full_path = os.path.join(quiz_applications_dir, quiz_dir)
        
        # Get buckets
        buckets = [d for d in os.listdir(quiz_full_path) 
                  if os.path.isdir(os.path.join(quiz_full_path, d))]
        
        directories_info[quiz_dir] = {"buckets": {}}
        
        for bucket in buckets:
            bucket_path = os.path.join(quiz_full_path, bucket)
            files = [f for f in os.listdir(bucket_path) if f.endswith('.html')]
            
            # Check for variant patterns
            variant_patterns = []
            for file in files:
                if 'variant-a-solution' in file.lower():
                    variant_patterns.append('a-solution')
                if 'variant-b-problem' in file.lower():
                    variant_patterns.append('b-problem')
                if 'variant-c-most-aware' in file.lower():
                    variant_patterns.append('c-most-aware')
                if 'variant-c-mostaware-long' in file.lower():
                    variant_patterns.append('c-mostaware-long')
            
            directories_info[quiz_dir]["buckets"][bucket] = {
                "files": files,
                "variants": variant_patterns
            }
    
    # Step 2: Process quiz HTML files
    print("\nChecking quiz HTML files for issues...")
    quiz_files = [f for f in os.listdir(niches_dir) if f.endswith('-quiz.html')]
    
    for quiz_file in quiz_files:
        print(f"\nProcessing {quiz_file}...")
        quiz_path = os.path.join(niches_dir, quiz_file)
        
        # Try to match with a directory
        quiz_name = quiz_file.replace('-quiz.html', '')
        matching_dir = None
        
        # Check special mappings first
        if quiz_name in special_mappings:
            matching_dir = special_mappings[quiz_name]
            print(f"  Special mapping found: {quiz_name} -> {matching_dir}")
        else:
            # Find the matching directory
            for dir_name in directories_info.keys():
                if dir_name in quiz_name or quiz_name in dir_name:
                    matching_dir = dir_name
                    break
        
        if not matching_dir:
            issues_found.append(f"Could not find matching directory for {quiz_file}")
            print(f"  ⚠️ No matching directory found for {quiz_file}")
            continue
            
        print(f"  Matches directory: {matching_dir}")
        
        # Read the file
        with open(quiz_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for URL construction
        if f"../quiz-applications/{matching_dir}" not in content:
            issues_found.append(f"URL in {quiz_file} does not reference correct directory {matching_dir}")
        
        # Apply fixes
        changes_made = False
        
        # Fix 1: c-most-aware vs c-mostaware-long
        content, fix1 = fix_c_most_aware_variant(quiz_file, content)
        changes_made = changes_made or fix1
        
        # Fix 2: URL construction directory
        content, fix2 = fix_url_construction(quiz_file, content, matching_dir)
        changes_made = changes_made or fix2
        
        # Fix 3: Filename pattern
        buckets = directories_info[matching_dir]["buckets"].keys()
        content, fix3 = fix_filename_pattern(quiz_file, content, matching_dir, buckets, directories_info[matching_dir])
        changes_made = changes_made or fix3
        
        # Save changes if any were made
        if changes_made:
            backup_file(quiz_path)
            with open(quiz_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixes_made.append(f"Fixed issues in {quiz_file}")
            print(f"  ✅ Fixed and saved changes to {quiz_file}")
        else:
            print(f"  ✓ No issues to fix in {quiz_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if not issues_found:
        print("No issues found that needed fixing!")
    else:
        print(f"Found {len(issues_found)} issues:")
        for issue in issues_found:
            print(f"- {issue}")
    
    if fixes_made:
        print(f"\nMade {len(fixes_made)} fixes:")
        for fix in fixes_made:
            print(f"✅ {fix}")
    else:
        print("\nNo fixes were necessary - everything looks good!")
    
    return fixes_made

if __name__ == "__main__":
    print("Quiz Redirect Fixer")
    print("="*20)
    fixes = fix_quiz_redirects() 