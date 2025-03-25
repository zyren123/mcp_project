from mcp.server.fastmcp import FastMCP
import os
mcp = FastMCP("ShellGenerator")


@mcp.tool()
def execute_shell_command(command: str) -> str:
    """
    Execute shell command
    
    Parameters:
        command: Shell command to execute
        
    Returns:
        Execution result
    """
    return os.popen(command).read()

if __name__ == "__main__":
    mcp.run(transport="stdio") 