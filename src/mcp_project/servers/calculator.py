#!/usr/bin/env python3
"""
Calculator Server Example
"""
from mcp.server.fastmcp import FastMCP
import numpy as np
# Create MCP server
mcp = FastMCP("Calculator")


# Add multiple numbers addition tool
@mcp.tool()
def add(numbers: list[float]) -> float:
    """
    Calculate the sum of multiple numbers
    
    Parameters:
        numbers: List of numbers to add
        
    Returns:
        Sum of all numbers
    """
    return sum(numbers)

@mcp.tool()
def multiply(numbers: list[float]) -> float:
    """
    Calculate the product of multiple numbers
    
    Parameters:
        numbers: List of numbers to multiply
        
    Returns:
        Product of all numbers
    """
    return np.prod(numbers)


@mcp.tool()
def compare(a: float, b: float) -> bool:
    """
    Compare two numbers
    
    Parameters:
        a: First number
        b: Second number
        
    Returns:
        True if a is greater than b, False otherwise
    """
    if a > b:
        return True
    else:
        return False
    

# Add greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    Get personalized greeting
    
    Parameters:
        name: Name
        
    Returns:
        Greeting message
    """
    return f"Hello, {name}! Welcome to the Calculator Server."


if __name__ == "__main__":
    mcp.run(transport="stdio") 