from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# 配置 python开发的mcp服务器的地址,可能有多个MCP服务器地址
python_mcp_server_config = {
    # 'url': 'http://127.0.0.1:8080/streamable',
    # 'transport': 'streamable_http',
    'url':'http://127.0.0.1:8080/sse',
    'transport':'sse'
}


