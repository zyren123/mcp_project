#!/usr/bin/env python3
"""
MCP Multi-Server Client Startup Script
"""
import asyncio
import sys
import os
import json
import argparse
from src.mcp_project import MultiServerClient

# Try to import dotenv
try:
    from dotenv import load_dotenv
    _has_dotenv = True
except ImportError:
    _has_dotenv = False

async def run(server_config_path: str = "config/servers.json", api_config_path: str = "config/api_config.json"):
    """
    Run the multi-server client
    
    Parameters:
        server_config_path: Path to the server configuration file
        api_config_path: Path to the API configuration file
    
    Returns:
        int: Exit code
    """
    # Try to load .env file
    if _has_dotenv:
        load_dotenv()
        print("Loaded .env file (if it exists)")
    else:
        print("Tip: Install python-dotenv package to support .env files")
    
    # Check critical environment variables
    if not os.getenv("OPENAI_API_KEY") and not os.path.exists(api_config_path):
        print("Warning: OPENAI_API_KEY environment variable not found and API config file does not exist")
        print("You can set the OPENAI_API_KEY environment variable or create a configuration file")
    
    # Check if server configuration file exists
    if not os.path.exists(server_config_path):
        print(f"Error: Server configuration file {server_config_path} does not exist")
        print("Please create the configuration file first")
        return 1
    
    # Validate server configuration file format
    try:
        with open(server_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print(f"Error: Configuration file {server_config_path} is invalid, missing 'mcpServers' section")
            return 1
    except json.JSONDecodeError:
        print(f"Error: Configuration file {server_config_path} is not valid JSON format")
        return 1
    except Exception as e:
        print(f"Error reading server configuration file: {str(e)}")
        return 1
    
    # Check if API configuration file exists (optional)
    if not os.path.exists(api_config_path):
        print(f"Warning: API configuration file {api_config_path} does not exist, will use environment variables or default settings")
    else:
        # Validate API configuration file format
        try:
            with open(api_config_path, "r", encoding="utf-8") as f:
                api_config = json.load(f)
            
            if "openai_api" not in api_config:
                print(f"Warning: API configuration file {api_config_path} is invalid, missing 'openai_api' section, will use environment variables or default settings")
            
            # Check if API key is empty
            if not api_config.get("openai_api", {}).get("api_key"):
                if os.getenv("OPENAI_API_KEY"):
                    print("Note: API key is empty in configuration file, will use OPENAI_API_KEY environment variable")
                else:
                    print("Warning: API key is empty in configuration file and OPENAI_API_KEY environment variable is not set")
        except json.JSONDecodeError:
            print(f"Warning: API configuration file {api_config_path} is not valid JSON format, will use environment variables or default settings")
        except Exception as e:
            print(f"Error reading API configuration file: {str(e)}, will use environment variables or default settings")
    
    # Create and initialize client
    client = MultiServerClient(server_config_path, api_config_path)
    try:
        # Initialize client
        if await client.initialize():
            # Run chat loop
            await client.chat_loop()
        else:
            print("Failed to initialize client")
            return 1
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        return 1
    finally:
        # Clean up resources
        await client.cleanup()
    
    return 0

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Multi-Server Client")
    parser.add_argument("--servers", "-s", help="Path to server configuration file", default="config/servers.json")
    parser.add_argument("--api", "-a", help="Path to API configuration file", default="config/api_config.json")
    args = parser.parse_args()
    
    print("Starting MCP Multi-Server Client...")
    print(f"Server configuration file: {args.servers}")
    print(f"API configuration file: {args.api}")
    
    # Run async main function
    exit_code = asyncio.run(run(args.servers, args.api))
    
    print("Client has exited")
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 