from mcp.server import FastMCP
import io
import contextlib

mcp = FastMCP("PythonExecutor")


def execute_python_code_with_capture(code: str):
    """
    Execute Python code and capture all stdout output

    This uses StringIO and contextlib.redirect_stdout for reliable stdout capturing

    Parameters:
        code: Python code to execute

    Returns:
        tuple: (success, output_or_error)
    """
    # Create a StringIO object to capture output
    f = io.StringIO()

    try:
        # Redirect stdout to our StringIO object
        with contextlib.redirect_stdout(f):
            # Execute the code
            exec(code, {})

        # Get the captured output
        output = f.getvalue()
        return True, output
    except Exception as e:
        return False, f"Error: {str(e)}"


@mcp.tool()
def execute_python_code(code: str) -> str:
    """
    Execute Python code and capture all stdout output

    Parameters:
        code: a string of python code

    Returns:
        Captured stdout output or error message
    """
    success, result = execute_python_code_with_capture(code)

    if success:
        if not result.strip():
            return "Code executed successfully. No output produced."
        return f"Code executed successfully. Output:\n{result}"
    else:
        return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
