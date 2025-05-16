import os
import re
import json

def check_directories_and_files():
    """Check all quiz directories and their associated files"""
    quiz_applications_dir = 'quiz-applications'
    niches_dir = 'niches'
    
    # Track issues to report
    issues = []
    
    # Step 1: Check all directories in quiz-applications
    print(f"Scanning {quiz_applications_dir} directory...")
    quiz_dirs = [d for d in os.listdir(quiz_applications_dir) 
                if os.path.isdir(os.path.join(quiz_applications_dir, d))]
    
    print(f"Found {len(quiz_dirs)} quiz application directories")
    
    # Dictionary to hold directory information
    directories_info = {}
    
    # Special mappings for mismatched directory and quiz names
    special_mappings = {
        "cosmetic-dentists": "cosmetic-dentistry"
    }
    
    # Step 2: Check each subdirectory for each quiz directory
    for quiz_dir in quiz_dirs:
        print(f"\nChecking {quiz_dir}...")
        quiz_full_path = os.path.join(quiz_applications_dir, quiz_dir)
        
        # Get subfolders (buckets)
        buckets = [d for d in os.listdir(quiz_full_path) 
                  if os.path.isdir(os.path.join(quiz_full_path, d))]
        
        if not buckets:
            issues.append(f"⚠️ No buckets found in {quiz_dir}")
            continue
            
        print(f"  Found buckets: {', '.join(buckets)}")
        directories_info[quiz_dir] = {"buckets": {}}
        
        # Step 3: Check each bucket for variant files
        for bucket in buckets:
            bucket_path = os.path.join(quiz_full_path, bucket)
            files = [f for f in os.listdir(bucket_path) if f.endswith('.html')]
            
            if not files:
                issues.append(f"⚠️ No HTML files found in {quiz_dir}/{bucket}")
                continue
                
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
            
            print(f"  {bucket} bucket has {len(files)} HTML files.")
            print(f"  Variants found: {', '.join(variant_patterns)}")
            
            directories_info[quiz_dir]["buckets"][bucket] = {
                "files": files,
                "variants": variant_patterns
            }
    
    # Step 4: Check quiz HTML files to see if they match the directory structure
    print("\n\nChecking quiz redirect URLs...")
    quiz_files = [f for f in os.listdir(niches_dir) if f.endswith('-quiz.html')]
    
    for quiz_file in quiz_files:
        print(f"\nChecking {quiz_file}...")
        quiz_path = os.path.join(niches_dir, quiz_file)
        
        # Try to determine which quiz application this corresponds to
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
            issues.append(f"⚠️ Could not find matching directory for {quiz_file}")
            continue
            
        print(f"  Matches directory: {matching_dir}")
        
        # Read the file to check the URL construction
        with open(quiz_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the URL construction line
        url_pattern = r'const url = `\.\.\/quiz-applications\/([^/]+)\/([^/]+)\/([^`]+)`'
        url_matches = re.findall(url_pattern, content)
        
        if not url_matches:
            issues.append(f"⚠️ Could not find URL construction in {quiz_file}")
            continue
            
        dir_in_url, bucket_var, file_pattern = url_matches[0]
        print(f"  URL points to: quiz-applications/{dir_in_url}/{bucket_var}/{file_pattern}")
        
        # Check if the directory matches
        if dir_in_url != matching_dir:
            issues.append(f"⚠️ URL uses wrong directory: {dir_in_url} instead of {matching_dir} in {quiz_file}")
        
        # Check bucket variable
        if "${scoreBucket}" not in bucket_var:
            issues.append(f"⚠️ URL doesn't use dynamic bucket variable in {quiz_file}")
        
        # Check if the file pattern will match actual files
        for bucket in directories_info[matching_dir]["buckets"]:
            # Get a sample file to check pattern against
            sample_files = directories_info[matching_dir]["buckets"][bucket]["files"]
            if not sample_files:
                continue
                
            # Check if the pattern with substitutions would match
            file_pattern_expanded = file_pattern.replace("${scoreBucket}", bucket)
            file_pattern_expanded = file_pattern_expanded.replace("${awarenessVariant}", "a-solution")
            sample_expanded = file_pattern_expanded.split('?')[0]  # Remove query params
            
            matching_file = False
            for f in sample_files:
                if sample_expanded in f or f in sample_expanded:
                    matching_file = True
                    break
            
            if not matching_file:
                issues.append(f"⚠️ URL pattern {sample_expanded} might not match actual files in {bucket} for {quiz_file}")
        
        # Check for specific variant issues
        for bucket in directories_info[matching_dir]["buckets"]:
            variants = directories_info[matching_dir]["buckets"][bucket]["variants"]
            
            # Look for c-most-aware vs c-mostaware-long issues
            if 'c-most-aware' in variants and 'c-mostaware-long' in variants:
                issues.append(f"⚠️ Mixed variant naming in {matching_dir}/{bucket}: both c-most-aware and c-mostaware-long")
            
            # Check if quiz refers to c-most-aware but files use c-mostaware-long
            if 'c-mostaware-long' in variants and 'c-most-aware' not in variants:
                if 'awarenessVariant = "c-most-aware"' in content:
                    issues.append(f"⚠️ Quiz uses 'c-most-aware' but files use 'c-mostaware-long' in {matching_dir}/{bucket}")
    
    # Print summary of issues
    print("\n\n" + "="*50)
    print("SUMMARY OF ISSUES")
    print("="*50)
    
    if not issues:
        print("✅ No issues found! All quizzes appear to be correctly configured.")
    else:
        print(f"Found {len(issues)} potential issues:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    
    return issues

if __name__ == "__main__":
    print("Quiz Redirect Checker")
    print("="*30)
    issues = check_directories_and_files() 