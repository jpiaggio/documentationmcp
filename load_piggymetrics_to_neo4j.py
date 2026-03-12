#!/usr/bin/env python3
"""
Load PiggyMetrics Maven modules into Neo4j for analysis.
Parses pom.xml files and creates a dependency graph.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set
import sys

# Try to import Neo4j
try:
    from neo4j import GraphDatabase
except ImportError:
    print("neo4j package not installed. Install with: pip install neo4j")
    sys.exit(1)


class PiggyMetricsLoader:
    def __init__(self, repo_path: str, neo4j_uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", password: str = "piggymetrics"):
        """Initialize Neo4j connection and load PiggyMetrics."""
        self.repo_path = Path(repo_path)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        self.modules: Dict[str, dict] = {}
        self.dependencies: List[tuple] = []
        
    def parse_pom_xml(self, pom_file: Path) -> dict:
        """Parse a pom.xml file and extract module info."""
        try:
            tree = ET.parse(pom_file)
            root = tree.getroot()
            
            # Handle Maven namespaces
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            
            # Try to get artifact ID
            artifact_id_elem = root.find('.//m:artifactId', ns)
            if artifact_id_elem is None:
                artifact_id_elem = root.find('.//artifactId')
            
            # Try to get name
            name_elem = root.find('.//m:name', ns)
            if name_elem is None:
                name_elem = root.find('.//name')
            
            # Try to get dependencies
            deps = []
            for dep in root.findall('.//m:dependency', ns):
                dep_artifact = dep.find('.//m:artifactId', ns)
                if dep_artifact is None:
                    dep_artifact = dep.find('.//artifactId')
                if dep_artifact is not None:
                    deps.append(dep_artifact.text)
            
            artifact_id = artifact_id_elem.text if artifact_id_elem is not None else "unknown"
            name = name_elem.text if name_elem is not None else artifact_id
            
            return {
                "artifact_id": artifact_id,
                "name": name,
                "path": str(pom_file),
                "dependencies": deps
            }
        except Exception as e:
            print(f"Error parsing {pom_file}: {e}")
            return None
    
    def discover_modules(self):
        """Discover all Maven modules in the repository."""
        print(f"Discovering modules in {self.repo_path}...")
        
        pom_files = list(self.repo_path.glob("**/pom.xml"))
        print(f"Found {len(pom_files)} pom.xml files")
        
        for pom_file in pom_files:
            module_info = self.parse_pom_xml(pom_file)
            if module_info:
                artifact_id = module_info["artifact_id"]
                self.modules[artifact_id] = module_info
                print(f"  ✓ {artifact_id}")
                
                # Record dependencies
                for dep in module_info.get("dependencies", []):
                    if dep in self.modules or dep in [m["artifact_id"] for m in self.modules.values()]:
                        self.dependencies.append((artifact_id, dep))
    
    def load_to_neo4j(self):
        """Load modules and dependencies into Neo4j."""
        print("\nLoading modules into Neo4j...")
        
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            print("  ✓ Cleared existing data")
            
            # Create module nodes
            for artifact_id, module_info in self.modules.items():
                session.run(
                    "CREATE (m:Module {id: $id, name: $name, path: $path})",
                    id=artifact_id,
                    name=module_info["name"],
                    path=module_info["path"]
                )
            print(f"  ✓ Created {len(self.modules)} module nodes")
            
            # Create dependency relationships
            dep_count = 0
            for source, target in self.dependencies:
                # Only create relationship if both modules exist
                if source in self.modules and target in self.modules:
                    session.run(
                        "MATCH (a:Module {id: $source}), (b:Module {id: $target}) "
                        "CREATE (a)-[:DEPENDS_ON]->(b)",
                        source=source,
                        target=target
                    )
                    dep_count += 1
            
            print(f"  ✓ Created {dep_count} dependency relationships")
            
            # Get statistics
            stats = session.run("MATCH (m:Module) RETURN COUNT(m) as modules").single()
            if stats:
                print(f"\nGraph Statistics:")
                print(f"  • Total modules: {stats['modules']}")
    
    def get_module_stats(self):
        """Get and print module statistics."""
        with self.driver.session() as session:
            # Get module list
            result = session.run("MATCH (m:Module) RETURN m.id, m.name ORDER BY m.id")
            print("\nModules loaded:")
            for record in result:
                print(f"  • {record['m.id']}")
    
    def close(self):
        """Close Neo4j connection."""
        self.driver.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 load_piggymetrics_to_neo4j.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    loader = PiggyMetricsLoader(repo_path)
    
    try:
        loader.discover_modules()
        loader.load_to_neo4j()
        loader.get_module_stats()
        
        print("\n✅ PiggyMetrics loaded into Neo4j successfully!")
        print("\nYou can now:")
        print("  • Browse Neo4j at http://localhost:7474")
        print("  • Query with Cypher: MATCH (m:Module) RETURN m")
        print("  • Find dependencies: MATCH (a)-[:DEPENDS_ON]->(b) RETURN a, b")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        loader.close()


if __name__ == "__main__":
    main()
