"""
Final Cleanup Script for UIDAI Project
=======================================
Removes duplicate path configurations and ensures proper imports
"""

import os
import re

def cleanup_file(filepath):
    """Remove duplicate path configurations and fix import issues"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match the path configuration block
    path_config_pattern = r"# Get the directory where this script is located\nSCRIPT_DIR = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n# Get the PROJECT directory \(parent of src\)\nPROJECT_PATH = os\.path\.dirname\(SCRIPT_DIR\)\n"
    
    # Count occurrences
    occurrences = len(re.findall(path_config_pattern, content))
    
    if occurrences > 1:
        # Remove all occurrences
        content = re.sub(path_config_pattern, '', content)
        
        # Find the right place to add it back (after 'import os')
        lines = content.split('\n')
        new_lines = []
        path_config_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add path config after 'import os' line
            if not path_config_added and 'import os' in line and not line.strip().startswith('#'):
                new_lines.append('')
                new_lines.append('# Get the directory where this script is located')
                new_lines.append('SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))')
                new_lines.append('# Get the PROJECT directory (parent of src)')
                new_lines.append('PROJECT_PATH = os.path.dirname(SCRIPT_DIR)')
                new_lines.append('')
                path_config_added = True
        
        content = '\n'.join(new_lines)
    
    # Ensure 'import os' exists
    if 'import os' not in content:
        # Add it at the beginning after docstring
        lines = content.split('\n')
        new_lines = []
        in_docstring = False
        docstring_closed = False
        
        for line in lines:
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                elif in_docstring and not docstring_closed:
                    docstring_closed = True
                    new_lines.append(line)
                    new_lines.append('')
                    new_lines.append('import os')
                    new_lines.append('')
                    new_lines.append('# Get the directory where this script is located')
                    new_lines.append('SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))')
                    new_lines.append('# Get the PROJECT directory (parent of src)')
                    new_lines.append('PROJECT_PATH = os.path.dirname(SCRIPT_DIR)')
                    continue
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("=" * 80)
    print("FINAL CLEANUP - Removing Duplicates")
    print("=" * 80)
    print()
    
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files except utility scripts
    python_files = [f for f in os.listdir(src_dir) 
                   if f.endswith('.py') and not f.startswith('fix_')]
    
    cleaned_count = 0
    for filename in sorted(python_files):
        filepath = os.path.join(src_dir, filename)
        print(f"Checking: {filename}...", end=' ')
        
        if cleanup_file(filepath):
            print("✓ CLEANED")
            cleaned_count += 1
        else:
            print("- OK")
    
    print()
    print("=" * 80)
    print(f"✅ Cleanup complete! Fixed {cleaned_count} files")
    print("=" * 80)

if __name__ == "__main__":
    main()
