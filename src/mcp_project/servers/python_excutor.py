from mcp.server import FastMCP

mcp = FastMCP("PythonExecutor")



@mcp.tool()
def execute_python_code(code: str) -> str:
    """
    Execute Python code
    
    Parameters:
        code: a string of python code
        
    Returns:
        Execution result
    """ 
    try:
        exec(code)
        return "Code executed successfully"
    except Exception as e:
        return f"Code execution failed: {e}"
    
    
if __name__ == "__main__":
    mcp.run(transport="stdio")
