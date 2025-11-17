"""
Automatically fixes all relative imports in the project.
Converts 'from module import' to 'from .module import'
"""
import os
import re

# Folders to fix
FOLDERS = ['orchestrator', 'memory', 'multiagent', 'trust_safety', 'evolution']

def fix_imports_in_file(file_path):
    """Fix imports in a single Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern: 'from module_name import' where module_name doesn't start with '.'
    # Replace with: 'from .module_name import'
    pattern = r'from ([a-z_][a-z0-9_]*) import'
    replacement = r'from .\1 import'
    
    content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {file_path}")
        return True
    return False

def main():
    """Fix all Python files in specified folders."""
    fixed_count = 0
    
    for folder in FOLDERS:
        folder_path = os.path.join(os.getcwd(), folder)
        
        if not os.path.exists(folder_path):
            print(f"⚠️  Folder not found: {folder}")
            continue
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if fix_imports_in_file(file_path):
                        fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files!")

if __name__ == '__main__':
    main()
