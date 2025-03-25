import subprocess
from mcp.server import FastMCP

mcp = FastMCP("PythonExecutor")



# @mcp.tool()
# def execute_python_code(code: str) -> str:
#     """
#     Execute Python code
    
#     Parameters:
#         code: a string of python code
        
#     Returns:
#         Execution result or error message
#     """ 
#     try:
#         return f"Code executed successfully, result: {exec(code)}"
#     except Exception as e:
#         return f"Code execution failed: {e}"
    
@mcp.tool()
def executor(python_code: str) -> str:
    """
    Execute Python code
    
    Parameters:
        python_code: a string of python code
        
    Returns:
        Execution result or error message
    """
    try:
        # Write Python code to a temporary file
        with open('temp_code.py', 'w', encoding='utf-8') as f:
            f.write(python_code)

        # Use subprocess module to execute the code in the temporary file
        result = subprocess.run(['python', 'temp_code.py'], capture_output=True, text=True, check=True)

        # Get standard output and standard error
        stdout = result.stdout
        stderr = result.stderr

        # If there is standard error output, return error message
        if stderr:
            return f"Execution error: {stderr}"

        # If no error, return standard output
        return stdout

    except subprocess.CalledProcessError as e:
        return f"Execution error: {e.stderr}"
    except Exception as e:
        return f"Unknown error occurred: {str(e)}"
    finally:
        # Delete temporary file
        import os
        if os.path.exists('temp_code.py'):
            os.remove('temp_code.py')

    
if __name__ == "__main__":
    mcp.run(transport="stdio")
