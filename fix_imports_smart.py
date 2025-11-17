"""
Intelligently fixes relative imports.
Only adds dots to local modules, NOT to Python standard library.
"""
import os
import re

STANDARD_LIBRARY = {
    'typing', 'datetime', 'os', 'sys', 'json', 're', 'logging', 'enum',
    'pathlib', 'collections', 'itertools', 'functools', 'random', 'string',
    'time', 'copy', 'pickle', 'stat', 'io', 'warnings', 'abc', 'asyncio',
    'threading', 'subprocess', 'socket', 'hashlib', 'hmac', 'base64', 'urllib',
    'csv', 'sqlite3', 'argparse', 'configparser', 'dataclasses', 'decimal',
    'fractions', 'numbers', 'cmath', 'statistics', 'difflib', 'pprint',
    'textwrap', 'unicodedata', 'struct', 'codecs', 'calendar', 'locale',
    'gettext', 'array', 'bisect', 'heapq', 'types', 'inspect', 'importlib',
    'graphlib', 'ast', 'symtable', 'token', 'keyword', 'tomllib', 'pydoc',
    'doctest', 'unittest', 'pdb', 'trace', 'tracemalloc', 'faulthandler',
    'cProfile', 'timeit', 'resource', 'sysconfig', 'platform', 'errno',
    'ctypes', 'select', 'selectors', 'asyncore', 'asynchat', 'ssl', 'email',
    'mailbox', 'imaplib', 'poplib', 'smtplib', 'uuid', 'http', 'ftplib',
    'poplib', 'nntplib', 'smtpd', 'telnetlib', 'socketserver', 'xmlrpc',
    'ipaddress', 'wave', 'chunk', 'sunau', 'aifc', 'colorsys', 'imghdr',
    'sndhdr', 'ossaudiodev', 'getopt', 'logging', 'getpass', 'curses',
    'platform', 'errno', 'ctypes', 'threading', 'multiprocessing', 'subprocess',
    'socket', 'ssl', 'select', 'selectors', 'asyncio', 'signal', 'mmap',
    'readline', 'rlcompleter', 'secrets', 'random', 'statistics', 'zlib',
    'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'csv', 'configparser',
    'netrc', 'xdrlib', 'plistlib', 'formatter', 'textwrap', 'pprint',
    'pydoc', 'doctest', 'unittest', 'mock', 'test', 'venv', 'zipimport',
    'pkgutil', 'modulefinder', 'runpy', 'ast', 'symtable', 'token', 'keyword',
    'tokenize', 'tabnanny', 'py_compile', 'compileall', 'dis', 'pickletools',
}

FOLDERS = ['orchestrator', 'memory', 'multiagent', 'trust_safety', 'evolution']

def fix_imports_in_file(file_path):
    """Fix imports in a single Python file, but NOT standard library."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix imports by checking if they're local modules
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip lines that don't have imports
        if not line.startswith('from ') or ' import ' not in line:
            fixed_lines.append(line)
            continue
        
        # Extract module name
        match = re.match(r'from (\.)?([a-z_][a-z0-9_]*)', line)
        if not match:
            fixed_lines.append(line)
            continue
        
        has_dot = match.group(1)
        module_name = match.group(2)
        
        # If it's standard library, remove dot
        if module_name in STANDARD_LIBRARY:
            fixed_line = line.replace(f'from .{module_name}', f'from {module_name}')
            fixed_lines.append(fixed_line)
        # If it's local and missing dot, add it
        elif not has_dot and module_name not in STANDARD_LIBRARY:
            fixed_line = line.replace(f'from {module_name}', f'from .{module_name}')
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    if fixed_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
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
