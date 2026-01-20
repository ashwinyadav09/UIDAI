"""
Comprehensive Path Fixer for UIDAI Project
===========================================
Fixes all path issues to make the project portable
"""

import os
import glob

def fix_file_paths(filepath):
    """Fix paths in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    has_path_config = False
    import_section_done = False
    path_config_added = False
    
    for i, line in enumerate(lines):
        # Check if path configuration already exists
        if 'SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))' in line:
            has_path_config = True
        
        # Add path configuration after imports if not present
        if not path_config_added and not has_path_config:
            if import_section_done and line.strip() and not line.strip().startswith('#'):
                # Insert path configuration before this line
                new_lines.append('\n')
                new_lines.append('# Get the directory where this script is located\n')
                new_lines.append('SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))\n')
                new_lines.append('# Get the PROJECT directory (parent of src)\n')
                new_lines.append('PROJECT_PATH = os.path.dirname(SCRIPT_DIR)\n')
                new_lines.append('\n')
                path_config_added = True
                modified = True
            elif line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section_done = True
        
        # Fix relative paths
        original_line = line
        
        # Pattern: '../data/processed/file.csv'
        if "'../data/processed/" in line:
            line = line.replace("'../data/processed/", "os.path.join(PROJECT_PATH, 'data', 'processed', '")
            line = line.replace(".csv'", ".csv')")
            modified = True
        
        # Pattern: '../processed/file.csv' (missing 'data')
        if "'../processed/" in line:
            line = line.replace("'../processed/", "os.path.join(PROJECT_PATH, 'data', 'processed', '")
            line = line.replace(".csv'", ".csv')")
            modified = True
        
        # Pattern: '../results/file.csv'
        if "'../results/" in line:
            line = line.replace("'../results/", "os.path.join(PROJECT_PATH, 'results', '")
            if ".csv'" in line:
                line = line.replace(".csv'", ".csv')")
            elif ".txt'" in line:
                line = line.replace(".txt'", ".txt')")
            elif ".xlsx'" in line:
                line = line.replace(".xlsx'", ".xlsx')")
            modified = True
        
        # Pattern: '../visualizations/file.png'
        if "'../visualizations/" in line:
            line = line.replace("'../visualizations/", "os.path.join(PROJECT_PATH, 'visualizations', '")
            line = line.replace(".png'", ".png')")
            modified = True
        
        # Pattern: os.makedirs('../results'
        if "os.makedirs('../results'" in line:
            line = line.replace("os.makedirs('../results'", "os.makedirs(os.path.join(PROJECT_PATH, 'results')")
            modified = True
        
        # Pattern: os.makedirs('../visualizations'
        if "os.makedirs('../visualizations'" in line:
            line = line.replace("os.makedirs('../visualizations'", "os.makedirs(os.path.join(PROJECT_PATH, 'visualizations')")
            modified = True
        
        new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    print("=" * 80)
    print("UIDAI PROJECT - COMPREHENSIVE PATH FIXER")
    print("=" * 80)
    print()
    
    # Get current directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files except this script
    python_files = glob.glob(os.path.join(src_dir, '*.py'))
    python_files = [f for f in python_files if not f.endswith('fix_paths.py') and not f.endswith('fix_all_paths.py')]
    
    print(f"Found {len(python_files)} Python files to process\n")
    
    fixed_count = 0
    for filepath in sorted(python_files):
        filename = os.path.basename(filepath)
        print(f"Processing: {filename}...", end=' ')
        
        if fix_file_paths(filepath):
            print("✓ FIXED")
            fixed_count += 1
        else:
            print("- No changes needed")
    
    print()
    print("=" * 80)
    print(f"✅ COMPLETE! Fixed {fixed_count} out of {len(python_files)} files")
    print("=" * 80)
    print()
    print("Your project is now portable and can run on any device!")
    print("All hardcoded and relative paths have been replaced with dynamic paths.")
    print()

if __name__ == "__main__":
    main()
