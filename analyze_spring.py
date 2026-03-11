#!/usr/bin/env python3
"""Analyze Spring Framework repository with Cartographer"""

import sys
sys.path.insert(0, '.')

from agents.cartographer_agent import cartographer_agent

print('Analyzing Spring Framework...')
results = cartographer_agent('/Users/juani/github-projects/spring-framework/spring-framework', file_ext='.java', max_workers=8)

# Count statement types
modules = len([s for s in results if ':Module' in s])
classes = len([s for s in results if ':Class' in s])
methods = len([s for s in results if ':Method' in s])
depends = len([s for s in results if 'DEPENDS_ON' in s])

print(f'''
Spring Framework Java Analysis Results
=====================================
Total Cypher statements: {len(results):,}
Modules (Java files):   {modules:,}
Classes:                {classes:,}
Methods:                {methods:,}
Dependencies:           {depends:,}
''')

# Extract unique module names
print('Sample modules found:')
sample_modules = set()
for stmt in results:
    if "MERGE (m:Module {name: '" in stmt:
        try:
            start = stmt.find("name: '") + 7
            end = stmt.find("'", start)
            module_name = stmt[start:end]
            sample_modules.add(module_name)
            if len(sample_modules) >= 10:
                break
        except:
            pass

for m in sorted(sample_modules):
    print(f'  - {m}')

print(f'\n✅ Successfully analyzed {modules:,} Java files from Spring Framework!')
