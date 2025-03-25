# MCP Multi-Server Client Project

A multi-server client project based on MCP (Model Control Protocol), supporting simultaneous connections to multiple servers and OpenAI API integration.

## Project Structure

```
mcp_project/
├── config/                   # Configuration directory
│   ├── servers.json          # Server configuration file (JSON format)
│   └── api_config.json       # API configuration file (JSON format)
├── src/                      # Source code directory
│   ├── __init__.py           # Package initialization
│   └── mcp_project/          # Main project package
│       ├── __init__.py       # Package initialization
│       ├── core/             # Core modules
│       │   ├── __init__.py   
│       │   ├── multi_server_client.py  # Multi-server client class
│       │   └── server_connection.py    # Server connection class
│       ├── servers/          # Server script directory
│       │   ├── __init__.py
│       │   ├── calculator.py           # Calculator server example
│       │   ├── fileprocessor.py        # File processing server
│       │   ├── python_excutor.py       # Python code execution server
│       │   └── shell_processor.py      # Shell command processor
│       └── utils/            # Utility functions
│           ├── __init__.py
│           └── load_config.py          # Configuration loading utilities
├── run.py                    # Startup script
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
├── .env.example              # Example environment variables (template)
├── .env                      # Environment variables file (optional)
└── README.md                 # Project documentation
```

## Features

1. **Multi-Server Support**: Connect to multiple MCP servers simultaneously based on JSON configuration
2. **Intelligent Tool Routing**: Automatically find servers that provide specific tools
3. **OpenAI API Integration**: Use OpenAI-compatible API interfaces (e.g., Qwen models)
4. **Interactive Interface**: Provides an interactive command-line interface
5. **Configurable API Settings**: Set API keys, models, and parameters via configuration files or environment variables
6. **Environment Variable Support**: Load configurations from .env files and system environment variables
7. **Code Execution**: Python code execution with captured output
8. **File Processing**: Read and write files
9. **Shell Command Execution**: Execute shell commands

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp_project.git
cd mcp_project

# Create and activate virtual environment (optional)
uv venv --python 3.12
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt
```

## Configuration

### Environment Variables

You can set environment variables in two ways:

1. **System Environment Variables**: Set them in your operating system
2. **.env File**: Create a `.env` file in the project root directory

Supported environment variables:
```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
OPENAI_TEMPERATURE=0.7
OPENAI_TOP_P=1.0
OPENAI_MAX_TOKENS=1000
OPENAI_TOOL_CHOICE=auto
```

Example `.env` file:
```
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
```

### Server Configuration

Edit the `config/servers.json` file to configure servers:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "src/mcp_project/servers/calculator.py"
      ],
      "name": "Calculator Server",
      "description": "Provides calculation functionality",
      "enable": true
    },
    "python_executor": {
      "command": "python",
      "args": [
        "src/mcp_project/servers/python_excutor.py"
      ],
      "name": "Python Executor",
      "description": "Executes Python code and captures output",
      "enable": true
    },
    "file_processor": {
      "command": "python",
      "args": [
        "src/mcp_project/servers/fileprocessor.py"
      ],
      "name": "File Processor",
      "description": "Provides file reading and writing functionality",
      "enable": true
    },
    "shell_processor": {
      "command": "python",
      "args": [
        "src/mcp_project/servers/shell_processor.py"
      ],
      "name": "Shell Processor",
      "description": "Executes shell commands",
      "enable": true
    }
  }
}
```

Each server configuration contains the following fields:
- `command`: Execution command (e.g., python or node)
- `args`: Command arguments array, usually starting with the server script path
- `name`: Display name (optional)
- `description`: Description (optional)
- `enable`: Whether the server is enabled (optional, defaults to true)

### API Configuration

Edit the `config/api_config.json` file to configure the OpenAI API:

```json
{
  "openai_api": {
    "api_key": "your-api-key",
    "base_url": "https://api.siliconflow.cn/v1",
    "model_name": "Qwen/Qwen2.5-7B-Instruct",
    "parameters": {
      "temperature": 0.7,
      "top_p": 1.0,
      "max_tokens": 1000,
      "tool_choice": "auto",
      "timeout": 60
    }
  }
}
```

**Note**:
- If the `api_key` field is empty, the system will use the `OPENAI_API_KEY` environment variable
- If the configuration file doesn't exist, the system will use environment variables or default values
- Configuration priority: Config file > Environment variables > Default values

## Running the Client

```bash
# Start with default configuration
python run.py

# Specify custom configuration paths
python run.py --servers path/to/servers.json --api path/to/api_config.json
```

The client provides an interactive command line interface. Type your queries and the client will process them using the OpenAI API and MCP servers.

## Available Servers and Tools

### Calculator Server
- `add`: Calculate the sum of multiple numbers
- `multiply`: Calculate the product of multiple numbers
- `compare`: Compare two numbers

### Python Executor
- `execute_python_code`: Execute Python code and capture stdout output
- `execute_with_globals`: Execute Python code with a customizable global namespace

### File Processor
- `read_file`: Read file content
- `write_file`: Write content to a file
- `list_files`: List files in a directory

### Shell Processor
- `execute_shell_command`: Execute shell commands