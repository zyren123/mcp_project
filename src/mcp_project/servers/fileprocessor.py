from mcp.server import FastMCP

mcp = FastMCP("FileProcessor")



@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read file content
    
    Parameters:
        file_path: Path to the file
        
    Returns:
        File content
    """
    return open(file_path, "r").read()

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    create a file and write content to it
    
    Parameters:
        file_path: Path to the file
        content: Content to write
    """
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return f"File {file_path} written successfully"
    except Exception as e:
        return f"File write failed: {e}"
        


if __name__ == "__main__":
    mcp.run(transport="stdio")



