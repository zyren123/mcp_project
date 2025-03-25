# MCP 多服务器客户端项目

这是一个基于MCP（Model Control Protocol）的多服务器客户端项目，支持同时连接多个服务器并使用OpenAI API进行调用。

## 项目结构

```
mcp_project/
├── config/                 # 配置文件目录
│   ├── servers.json        # 服务器配置文件(JSON格式)
│   └── api_config.json     # API配置文件(JSON格式)
├── mcp_client/             # 客户端包
│   ├── __init__.py         # 包初始化文件
│   ├── core/               # 核心模块
│   │   ├── __init__.py
│   │   ├── multi_server_client.py # 多服务器客户端类
│   │   └── server_connection.py  # 服务器连接类
│   ├── servers/            # 服务器脚本目录
│   │   └── add_server.py   # 加法服务器示例
│   └── utils/              # 工具函数目录
├── server.py               # 默认示例服务器
├── run.py                  # 启动脚本
├── pyproject.toml          # 项目配置
├── .env                    # 环境变量文件（可选）
└── README.md               # 项目说明
```

## 功能特点

1. **多服务器支持**: 根据JSON配置文件同时连接多个MCP服务器
2. **智能工具调用**: 自动寻找提供特定工具的服务器
3. **OpenAI API集成**: 使用OpenAI兼容的API接口（例如千问模型）
4. **交互式对话**: 提供交互式命令行界面
5. **可配置API设置**: 通过配置文件或环境变量设置API密钥、模型和参数
6. **环境变量支持**: 支持从.env文件和系统环境变量加载配置

## 安装依赖

```bash
# 创建和激活虚拟环境（可选）
uv venv --python 3.12
.venv\Scripts\activate
uv pip install -r reuqirements.txt


```

## 配置

### 环境变量配置

您可以通过以下两种方式设置环境变量：

1. **系统环境变量**：在操作系统中设置环境变量
2. **.env文件**：在项目根目录创建`.env`文件

支持的环境变量：
```
OPENAI_API_KEY=您的API密钥
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
OPENAI_TEMPERATURE=0.7
OPENAI_TOP_P=1.0
OPENAI_MAX_TOKENS=1000
OPENAI_TOOL_CHOICE=auto
```

.env文件示例：
```
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
```

### 服务器配置

编辑`config/servers.json`文件以配置服务器：

```json
 "mcpServers": {
    "add_server": {
      "command": "python",
      "args": [
        "mcp_client/servers/add_server.py"
      ],
      "name": "加法服务器",
      "description": "提供加法计算功能",
      "enable": true
    }}
```

每个服务器配置包含以下字段：
- `command`: 执行命令（如 python 或 node）
- `args`: 命令参数数组，第一个通常是服务器脚本路径
- `name`: 显示名称（可选）
- `description`: 描述（可选）
- `enable`: 是否启用（可选，默认为true）

### API配置

编辑`config/api_config.json`文件以配置OpenAI API：

```json
{
  "openai_api": {
    "api_key": "您的API密钥",
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

**注意**：
- 如果`api_key`字段为空，系统将使用环境变量`OPENAI_API_KEY`
- 如果配置文件不存在，系统将使用环境变量或默认值
- 环境变量的优先级：配置文件 > 环境变量 > 默认值

## 运行客户端

```bash
# 使用默认配置启动
python run.py

# 指定配置文件路径
python run.py --servers path/to/servers.json --api path/to/api_config.json

# 使用简写参数
python run.py -s path/to/servers.json -a path/to/api_config.json
```

## 开发指南

### 添加新服务器

1. 创建新的服务器脚本（例如`mcp_client/servers/new_server.py`）
2. 在服务器脚本中添加工具和资源
3. 在`config/servers.json`中添加服务器配置

### 扩展客户端功能

可以通过修改`mcp_client/core/multi_server_client.py`来扩展客户端功能，例如：

- 添加更多的API集成
- 实现图形用户界面
- 添加高级错误处理和日志记录

### 环境变量配置优先级

配置值的加载优先级如下：
1. 配置文件中的值
2. 环境变量
3. 默认值

例如，对于API密钥：
- 如果`api_config.json`中设置了`api_key`，则使用该值
- 如果`api_config.json`中`api_key`为空或不存在，则使用环境变量`OPENAI_API_KEY`
- 如果环境变量`OPENAI_API_KEY`也不存在，则为空（您可能需要手动设置）

## 示例代码

### 服务器配置示例

```json
{
  "mcpServers": {
    "default": {
      "command": "python",
      "args": [
        "server.py"
      ],
      "name": "默认服务器",
      "description": "主要功能服务器",
      "enable": true
    },
    "add_server": {
      "command": "python",
      "args": [
        "mcp_client/servers/add_server.py"
      ],
      "name": "加法服务器",
      "description": "提供加法计算功能",
      "enable": true
    },
    "markdown": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/mcp_servers",
        "run",
        "markdown_processor.py"
      ],
      "name": "Markdown处理器",
      "description": "处理Markdown文件",
      "enable": true
    }
  }
}
```

### API配置示例

```json
{
  "openai_api": {
    "api_key": "sk-your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model_name": "gpt-3.5-turbo",
    "parameters": {
      "temperature": 0.5,
      "top_p": 0.9,
      "max_tokens": 2000,
      "presence_penalty": 0.1,
      "frequency_penalty": 0.1,
      "tool_choice": "auto"
    }
  }
}
```
