# MCP 项目演示

这是一个使用MCP（Model Control Protocol）进行客户端-服务器通信的演示项目。

## 项目结构

- `server.py`: 服务器端实现，提供添加工具和问候资源
- `client.py`: 客户端实现，连接到服务器并使用其功能
- `main.py`: 主入口点

## 功能介绍

本演示实现了两个简单功能：
1. 加法工具：将两个整数相加
2. 问候资源：基于提供的名称生成个性化问候

## 如何运行

### 1. 准备环境

确保已安装Python和所需的依赖：

```bash
# 创建和激活虚拟环境（可选）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install mcp-python fastmcp
```

### 2. 启动服务器

在一个终端窗口中运行：

```bash
python server.py
```

### 3. 运行客户端

在另一个终端窗口中运行：

```bash
python client.py
```

## 扩展

您可以通过以下方式扩展此演示：
1. 在服务器中添加更多工具和资源
2. 修改客户端以使用这些新功能
3. 实现更复杂的业务逻辑
