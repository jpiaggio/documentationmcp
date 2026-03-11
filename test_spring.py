#!/usr/bin/env python3
"""Quick test of Spring Framework with Java support"""
import sys
sys.path.insert(0, '.')

from agents.cartographer_agent import cartographer_agent

print("Scanning Spring Framework for Java files (this may take a minute)...")
results = cartographer_agent(
    '/Users/juani/github-projects/spring-framework/spring-framework',
    file_ext='.java',
    max_workers=8
)

# Quick count
modules = sum(1 for s in results if ':Module' in s)
classes = sum(1 for s in results if ':Class' in s)  
methods = sum(1 for s in results if ':Method' in s)

print(f"\n✅ Spring Framework Analysis Complete!\n")
print(f"Total Cypher statements generated: {len(results):,}")
print(f"Java source files analyzed:        {modules:,}")
print(f"Classes discovered:                {classes:,}")
print(f"Methods/constructors found:        {methods:,}")
print(f"\nAverage methods per class: {methods/classes if classes > 0 else 0:.1f}")
