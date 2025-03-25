"""
Single Server Connection Module
"""
from pathlib import Path
from typing import Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ServerConnection:
    """Single Server Connection Class"""
    
    def __init__(self, server_id: str, config: dict):
        """
        Initialize server connection
        
        Parameters:
            server_id: Server ID
            config: Server configuration dictionary
        """
        self.server_id = server_id
        self.name = config.get("name", server_id)
        self.description = config.get("description", "")
        self.command = config.get("command", "python")
        self.args = config.get("args", [])
        self.enabled = config.get("enable", True)
        
        # Initialize session
        self.session: Optional[ClientSession] = None
        self.exit_stack = None
        self.tools = []
        self.resources = []
    
    async def connect(self, exit_stack: AsyncExitStack):
        """
        Connect to the server
        
        Parameters:
            exit_stack: Async exit stack
            
        Returns:
            bool: Whether connection was successful
        """
        if not self.enabled:
            print(f"Server {self.name} ({self.server_id}) is disabled, skipping connection")
            return False
        
        # Check if the first argument (script path) exists
        if self.args and not Path(self.args[0]).exists():
            print(f"Error: Server script {self.args[0]} does not exist, skipping connection")
            return False
        
        try:
            self.exit_stack = exit_stack
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args,
                env=None
            )
            
            # Connect to server
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            self.session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            
            # Initialize connection
            await self.session.initialize()
            
            # Get tools and resources list
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            resources_response = await self.session.list_resources()
            self.resources = resources_response.resources
            
            print(f"Successfully connected to server {self.name} ({self.server_id})")

            
            return True
        except Exception as e:
            print(f"Error connecting to server {self.name} ({self.server_id}): {str(e)}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call a tool
        
        Parameters:
            tool_name: Tool name
            arguments: Tool arguments
            
        Returns:
            Any: Tool call result
        """
        if not self.session:
            raise ValueError(f"Server {self.name} ({self.server_id}) is not connected")
        
        return await self.session.call_tool(tool_name, arguments)
    
    async def read_resource(self, resource_path: str) -> tuple:
        """
        Read a resource
        
        Parameters:
            resource_path: Resource path
            
        Returns:
            tuple: (content, MIME type)
        """
        if not self.session:
            raise ValueError(f"Server {self.name} ({self.server_id}) is not connected")
        
        return await self.session.read_resource(resource_path)
    
    def has_tool(self, tool_name: str) -> bool:
        """
        Check if the server has a specific tool
        
        Parameters:
            tool_name: Tool name
            
        Returns:
            bool: Whether the server has the tool
        """
        return any(tool.name == tool_name for tool in self.tools)
    
    def get_tool_schema(self, tool_name: str) -> Optional[dict]:
        """
        Get the input schema for a tool
        
        Parameters:
            tool_name: Tool name
            
        Returns:
            Optional[dict]: Tool input schema
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.inputSchema
        return None 
    
