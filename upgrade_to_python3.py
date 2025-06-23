#!/usr/bin/env python3
"""
Script to upgrade Datmo codebase from Python 2/3 compatibility to Python 3.x only
"""

import os
import re
import glob
from pathlib import Path

def upgrade_file(filepath):
    """Upgrade a single Python file to Python 3.x"""
    print(f"Upgrading: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove __future__ imports
    content = re.sub(r'^from __future__ import .*\n', '', content, flags=re.MULTILINE)
    
    # Fix str -> str (Python 2 compatibility)
    content = re.sub(r'\bbasestring\b', 'str', content)
    
    # Fix str -> str (Python 2 compatibility)
    content = re.sub(r'\bunicode\b', 'str', content)
    
    # Fix range -> range (Python 2 compatibility)
    content = re.sub(r'\bxrange\b', 'range', content)
    
    # Fix iteritems() -> items() (Python 2 compatibility)
    content = re.sub(r'\.iteritems\(\)', '.items()', content)
    
    # Fix iterkeys() -> keys() (Python 2 compatibility)
    content = re.sub(r'\.iterkeys\(\)', '.keys()', content)
    
    # Fix itervalues() -> values() (Python 2 compatibility)
    content = re.sub(r'\.itervalues\(\)', '.values()', content)
    
    # Fix collections imports (already done in misc_functions.py but apply globally)
    if 'import collections' in content and 'collections.abc' not in content:
        content = re.sub(
            r'import collections\n',
            'try:\n    from collections.abc import Mapping, Iterable\nexcept ImportError:\n    from collections import Mapping, Iterable\nimport collections\n',
            content
        )
        content = re.sub(r'collections\.Mapping', 'Mapping', content)
        content = re.sub(r'collections\.Iterable', 'Iterable', content)
    
    # Remove empty lines left by __future__ import removal
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
        return True
    else:
        print(f"  - No changes needed for {filepath}")
        return False

def main():
    """Main upgrade function"""
    datmo_root = Path(__file__).parent
    python_files = list(datmo_root.glob('**/*.py'))
    
    print(f"Found {len(python_files)} Python files to upgrade")
    print("=" * 50)
    
    updated_count = 0
    for py_file in python_files:
        if upgrade_file(py_file):
            updated_count += 1
    
    print("=" * 50)
    print(f"Upgrade complete! Updated {updated_count} files out of {len(python_files)} total files.")

if __name__ == "__main__":
    main()
