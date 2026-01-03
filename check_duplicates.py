#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check for duplicate keys in i18n.py TRANSLATIONS dictionary"""

import ast

def check_duplicate_keys():
    """Check for duplicate keys in TRANSLATIONS dictionary"""
    with open('i18n.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the file content
    tree = ast.parse(content)
    
    # Find the TRANSLATIONS dictionary
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'TRANSLATIONS':
                    if isinstance(node.value, ast.Dict):
                        keys = []
                        duplicate_keys = set()
                        
                        # Check each key
                        for key_node in node.value.keys:
                            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                                key = key_node.value
                                if key in keys:
                                    duplicate_keys.add(key)
                                keys.append(key)
                        
                        if duplicate_keys:
                            print(f"发现重复键: {', '.join(sorted(duplicate_keys))}")
                        else:
                            print("未发现重复键")
                        return
    
    print("未找到 TRANSLATIONS 字典")

if __name__ == "__main__":
    check_duplicate_keys()
