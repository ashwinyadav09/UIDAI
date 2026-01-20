"""
Path Fixer Script for UIDAI Project
====================================
This script fixes all hardcoded and relative paths in Python files
to make the project portable across different devices.
"""

import os
import re

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = SCRIPT_DIR

# Path configuration template to add to files
PATH_CONFIG_TEMPLATE = """# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the PROJECT directory (parent of src)
PROJECT_PATH = os.path.dirname(SCRIPT_DIR)
"""

def fix_relative_paths_in_file(filepath):
    """
    Fix relative paths in a Python file by replacing '../' with proper os.path.join
    """
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Check if path configuration already exists
    has_path_config = 'SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))' in content
    
    if not has_path_config:
        # Find the import section (after imports, before first function/class)
        import_section_end = 0
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section_end = i + 1
            elif import_section_end > 0 and line.strip() and not line.strip().startswith('#'):
                # Found first non-import, non-comment line
                break
        
        # Insert path configuration after imports
        if import_section_end > 0:
            lines.insert(import_section_end, '\n' + PATH_CONFIG_TEMPLATE)
            content = '\n'.join(lines)
    
    # Replace relative paths with os.path.join
    # Pattern 1: '../data/processed/...'
    content = re.sub(
        r"'\.\.\/data\/processed\/([^']+)'",
        r"os.path.join(PROJECT_PATH, 'data', 'processed', '\1')",
        content
    )
    
    # Pattern 2: '../results/...'
    content = re.sub(
        r"'\.\.\/results\/([^']+)'",
        r"os.path.join(PROJECT_PATH, 'results', '\1')",
        content
    )
    
    # Pattern 3: '../visualizations/...'
    content = re.sub(
        r"'\.\.\/visualizations\/([^']+)'",
        r"os.path.join(PROJECT_PATH, 'visualizations', '\1')",
        content
    )
    
    # Pattern 4: Create directories
    content = re.sub(
        r"os\.makedirs\('\.\.\/results'",
        r"os.makedirs(os.path.join(PROJECT_PATH, 'results')",
        content
    )
    
    content = re.sub(
        r"os\.makedirs\('\.\.\/visualizations'",
        r"os.makedirs(os.path.join(PROJECT_PATH, 'visualizations')",
        content
    )
    
    # Check if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Fixed paths in {os.path.basename(filepath)}")
        return True
    else:
        print(f"  - No changes needed for {os.path.basename(filepath)}")
        return False

def main():
    print("=" * 80)
    print("UIDAI PROJECT - PATH FIXER")
    print("=" * 80)
    print("\nThis script will fix all relative paths in Python files to make")
    print("the project portable across different devices.\n")
    
    # Get all Python files in src directory
    python_files = [
        os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR)
        if f.endswith('.py') and f != 'fix_paths.py'
    ]
    
    print(f"Found {len(python_files)} Python files to process\n")
    
    fixed_count = 0
    for filepath in sorted(python_files):
        if fix_relative_paths_in_file(filepath):
            fixed_count += 1
    
    print("\n" + "=" * 80)
    print(f"✅ PATH FIXING COMPLETE!")
    print("=" * 80)
    print(f"\nFixed {fixed_count} out of {len(python_files)} files")
    print("\nYour project is now portable and can run on any device!")
    print("=" * 80)

if __name__ == "__main__":
    main()
