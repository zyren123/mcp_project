"""
Multi-Server Client Core Module
"""
import json
import os
from typing import Dict, Optional, Any
from contextlib import AsyncExitStack
from openai import OpenAI
from ..utils.load_config import load_api_config
from pprint import pp
# Import dotenv support
try:
    from dotenv import load_dotenv
    _has_dotenv = True
except ImportError:
    _has_dotenv = False

from .server_connection import ServerConnection


class MultiServerClient:
    """Multi-Server Client Class"""
    
    def __init__(self, config_path: str = "config/servers.json", api_config_path: str = "config/api_config.json"):
        """
        Initialize multi-server client
        
        Parameters:
            config_path: Path to server configuration file
            api_config_path: Path to API configuration file
        """
        # Try to load .env file
        if _has_dotenv:
            load_dotenv()
        
        # Initialize variables
        self.servers: Dict[str, ServerConnection] = {}
        self.config_path = config_path
        self.api_config_path = api_config_path
        self.exit_stack = AsyncExitStack()
        
        # Load API configuration
        self.api_config = load_api_config(self.api_config_path)
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_config.get("openai_api", {}).get("api_key", os.getenv("OPENAI_API_KEY")),
            base_url=self.api_config.get("openai_api", {}).get("base_url", os.getenv("OPENAI_BASE_URL"))
        )
        
        # Get model name and parameters
        self.model_name = self.api_config.get("openai_api", {}).get("model_name", os.getenv("OPENAI_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct"))
        self.api_parameters = self.api_config.get("openai_api", {}).get("parameters", {})
    

    
    async def initialize(self):
        """
        Initialize client and connect to all servers
        
        Returns:
            bool: Whether initialization was successful
        """
        # Load configuration
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            # Get server configurations
            server_configs = config_data.get("mcpServers", {})
            if not server_configs:
                print(f"Warning: 'mcpServers' section not found in configuration file")
                return False
                
        except Exception as e:
            print(f"Error loading configuration file: {str(e)}")
            return False
        total_tools=[]
        total_resources=[]
        # Create server connections
        for server_id, server_config in server_configs.items():
            server = ServerConnection(server_id, server_config)
            self.servers[server_id] = server
        
        # Connect to all servers
        connected_servers = 0
        for server_id, server in self.servers.items():
            if await server.connect(self.exit_stack):
                connected_servers += 1
                total_tools.extend(server.tools)
                total_resources.extend(server.resources)
        if connected_servers == 0:
            print("Warning: Failed to connect to any servers")
            return False
        
        print(f"Successfully connected to {connected_servers}/{len(self.servers)} servers.")
        pp(f"Available tools: { [tool.name for tool in total_tools]}")
        pp(f"Available resources: { [resource.pattern for resource in total_resources]}")
        return True
    
    def find_server_for_tool(self, tool_name: str) -> Optional[ServerConnection]:
        """
        Find server that provides the specified tool
        
        Parameters:
            tool_name: Tool name
            
        Returns:
            Optional[ServerConnection]: Server that provides the tool
        """
        for server in self.servers.values():
            if server.has_tool(tool_name):
                return server
        return None
    
    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call any available tool
        
        Parameters:
            tool_name: Tool name
            arguments: Tool arguments
            
        Returns:
            Any: Tool call result
        """
        server = self.find_server_for_tool(tool_name)
        if not server:
            raise ValueError(f"No server provides tool '{tool_name}'")
        
        return await server.call_tool(tool_name, arguments)
    
    async def process_query(self, query: str) -> str:
        """
        Process query using OpenAI API and call available tools
        
        Parameters:
            query: User query
            
        Returns:
            str: Processing result
        """
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        # Collect tools from all servers
        available_tools = []
        for server in self.servers.values():
            for tool in server.tools:
                available_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
        
        print(f"Total available tools: {len(available_tools)}")
        print("Initial messages:", messages)
        
        # Process results and possible tool calls
        final_text = []
        
        while True:
            # Call OpenAI API
            print("Calling OpenAI API...")
            
            # Prepare API parameters
            api_params = self.api_parameters.copy()
            api_params.update({
                "model": self.model_name,
                "messages": messages,
                "tools": available_tools
            })
            
            response = self.client.chat.completions.create(**api_params)
            
            # Get model response
            assistant_message = response.choices[0].message
            assistant_content = assistant_message.content
            
            # If there is text content, add to final result
            if assistant_content:
                final_text.append(assistant_content)
                print(f"Model response: {assistant_content}")
            
            # Check if there are tool calls
            tool_calls = assistant_message.tool_calls
            if not tool_calls:
                # No tool calls, end conversation
                break
                
            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                
                print(f"Calling tool: {function_name}, arguments: {function_args}")
                
                # Execute tool call
                try:
                    # Convert string JSON to Python dictionary
                    args_dict = json.loads(function_args)
                    
                    # Call tool
                    result = await self.call_tool(function_name, args_dict)
                    final_text.append(f"[Called tool {function_name} with arguments {function_args}]")
                    
                    # Add tool call result to message history
                    messages.append({
                        "role": "assistant",
                        "content": assistant_content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": function_args
                                }
                            }
                        ]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)  # Ensure result is a string
                    })
                    
                    print(f"Tool returned result: {result}")
                except Exception as e:
                    error_msg = f"Tool call failed: {str(e)}"
                    final_text.append(error_msg)
                    print(error_msg)
                    
                    # Add error information to message history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: {str(e)}"
                    })
            
            # Continue conversation loop, let model process tool call results
        
        # Return all results
        return "\n".join(final_text)
    
    async def chat_loop(self):
        """
        Run interactive conversation loop
        """
        print("\nMCP Multi-Server Client started!")
        print("Enter query or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """
        Clean up resources
        """
        await self.exit_stack.aclose() 