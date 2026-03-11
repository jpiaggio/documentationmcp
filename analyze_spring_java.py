#!/usr/bin/env python3
"""Analyze Spring Framework Java files using cartographer agent."""

import sys
from agents.cartographer_agent import cartographer_agent

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_spring_java.py <repo_path> [max_workers]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    print(f"Analyzing Spring Framework Java files from: {repo_path}", file=__import__('sys').stderr)
    print(f"Using {max_workers} workers", file=__import__('sys').stderr)
    
    try:
        # Analyze Java files with business rules extraction
        cypher_statements = cartographer_agent(
            repo_path, 
            file_ext='.java',  # Java files only
            max_workers=max_workers,
            use_business_rules=True
        )
        
        print(f"\n=== Analysis Complete ===", file=__import__('sys').stderr)
        print(f"Generated {len(cypher_statements)} insights/statements", file=__import__('sys').stderr)
        
        # Output all statements
        for stmt in cypher_statements:
            print(stmt)
            
    except Exception as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
        import traceback
        traceback.print_exc(file=__import__('sys').stderr)
        sys.exit(1)
