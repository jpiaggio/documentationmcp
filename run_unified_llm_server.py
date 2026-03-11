#!/usr/bin/env python3
"""
Unified LLM Query Interface - MCP Server Wrapper

Wraps the unified query interface as a proper MCP server so Claude and other
MCP clients can use all query capabilities seamlessly.

Usage:
    python3 run_unified_llm_server.py /path/to/repo
"""

import json
import sys
from pathlib import Path

try:
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, TextContent, ToolResult
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not installed. Install with: pip install mcp", file=sys.stderr)

sys.path.insert(0, str(Path(__file__).parent))

from unified_llm_query_interface import (
    UnifiedLLMQueryInterface,
    create_mcp_tools
)


class UnifiedLLMServer(Server):
    """MCP Server wrapper for unified LLM query interface."""
    
    def __init__(self, repository_path: str):
        """Initialize the server with a repository."""
        super().__init__("unified-llm-query")
        
        self.interface = UnifiedLLMQueryInterface(repository_path)
        self.tools = create_mcp_tools(self.interface)
        
        # Register tools
        for tool_def in self.tools:
            self.add_tool(tool_def)
    
    def add_tool(self, tool_def: dict):
        """Add a tool to the server."""
        tool = Tool(
            name=tool_def["name"],
            description=tool_def["description"],
            inputSchema=tool_def["inputSchema"]
        )
        
        # Register the handler
        self.register_tool(tool_def["name"], self.handle_tool_call)
    
    def register_tool(self, name: str, handler):
        """Register a tool handler."""
        if not hasattr(self, '_tools'):
            self._tools = {}
        self._tools[name] = handler
    
    async def handle_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Handle tool calls from MCP clients."""
        try:
            if tool_name == "query":
                result = self.interface.query(tool_input.get("query", ""))
            
            elif tool_name == "list_modules":
                result = self.interface.list_modules()
            
            elif tool_name == "find_function":
                result = self.interface.find_function(tool_input.get("function_name", ""))
            
            elif tool_name == "get_dependencies":
                result = self.interface.get_dependencies(tool_input.get("module_name", ""))
            
            elif tool_name == "get_business_rules":
                result = self.interface.get_business_rules(
                    tool_input.get("rule_type")
                )
            
            elif tool_name == "get_customer_journey":
                result = self.interface.get_customer_journey()
            
            elif tool_name == "get_business_entities":
                result = self.interface.get_business_entities(
                    tool_input.get("entity_type")
                )
            
            elif tool_name == "analyze_code_semantics":
                result = self.interface.analyze_code_semantics(
                    tool_input.get("code", ""),
                    tool_input.get("filename")
                )
            
            elif tool_name == "ask_question":
                result = self.interface.ask_question(
                    tool_input.get("question", ""),
                    tool_input.get("code")
                )
            
            elif tool_name == "trace_data_flow":
                result = self.interface.trace_data_flow(
                    tool_input.get("source", ""),
                    tool_input.get("target", "")
                )
            
            elif tool_name == "find_circular_dependencies":
                result = self.interface.find_circular_dependencies()
            
            else:
                return json.dumps({
                    "error": f"Unknown tool: {tool_name}",
                    "success": False
                })
            
            return json.dumps(result.to_dict())
        
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "success": False,
                "tool": tool_name
            })


async def main():
    """Main entry point for MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP library not installed", file=sys.stderr)
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python3 run_unified_llm_server.py <repo_path>", file=sys.stderr)
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    print(f"Starting Unified LLM Query Server for {repo_path}", file=sys.stderr)
    
    server = UnifiedLLMServer(repo_path)
    
    async with stdio_server(server) as (read_stream, write_stream):
        print("Server running. Press Ctrl+C to stop.", file=sys.stderr)
        await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
