#!/usr/bin/env python3
"""
Helper script to load cartographer results into Neo4j and manage the MCP server.
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

def load_cartographer_results(repo_path: str, neo4j_uri: str = "bolt://localhost:7687", 
                              neo4j_user: str = "neo4j", neo4j_password: str = "password"):
    """Load cartographer results into Neo4j."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("neo4j package not installed. Install with: pip install neo4j")
        sys.exit(1)
    
    print(f"Generating Cypher statements from {repo_path}...")
    
    # Run cartographer agent
    result = subprocess.run(
        ["python3", "agents/cartographer_agent.py", repo_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running cartographer agent: {result.stderr}")
        sys.exit(1)
    
    # Parse output to get Cypher statements
    cypher_statements = []
    for line in result.stdout.split('\n'):
        if line.startswith('MERGE'):
            cypher_statements.append(line.strip())
    
    if not cypher_statements:
        print("No Cypher statements generated.")
        return
    
    print(f"Generated {len(cypher_statements)} Cypher statements")
    print(f"Connecting to Neo4j at {neo4j_uri}...")
    
    # Connect to Neo4j and load statements
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        with driver.session() as session:
            for stmt in cypher_statements:
                try:
                    session.run(stmt)
                except Exception as e:
                    print(f"Warning: Failed to execute statement: {e}")
        
        print(f"Successfully loaded {len(cypher_statements)} statements into Neo4j")
        driver.close()
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
        print("\nMake sure Neo4j is running. You can start it with:")
        print(f"  docker run -p 7687:7687 -p 7474:7474 --name neo4j-cartographer neo4j")
        sys.exit(1)


def start_mcp_server():
    """Start the Neo4j MCP server."""
    print("\nStarting MCP server...")
    subprocess.run(["python3", "mcp_neo4j_server.py", "stdio"])


def main():
    parser = argparse.ArgumentParser(
        description="Manage cartographer results with Neo4j and MCP"
    )
    parser.add_argument("repo_path", help="Path to the repository to analyze")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", 
                        help="Neo4j connection URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="password", help="Neo4j password")
    parser.add_argument("--skip-load", action="store_true", 
                        help="Skip loading cartographer results")
    
    args = parser.parse_args()
    
    if not args.skip_load:
        load_cartographer_results(
            args.repo_path,
            args.neo4j_uri,
            args.neo4j_user,
            args.neo4j_password
        )
    
    start_mcp_server()


if __name__ == "__main__":
    main()
