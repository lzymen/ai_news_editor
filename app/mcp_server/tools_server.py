from typing import Annotated

from fastmcp import FastMCP
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
import asyncio
from app.core.env_utils import WEB_SEARCH_URL

server = FastMCP(name='mcp_server',instructions="这是一个进行对mcp服务器的测试")

# 负责测试搜索功能能否成功
async def search_logic(query: str, limit: int = 3) -> str:
    """
    这是纯粹的搜索逻辑，普通的 Python 函数，可以直接调用测试。
    """
    # Node 服务地址
    node_server_url = "http://localhost:3000/sse"

    try:
        # 建立与 Node.js 服务器的连接
        async with sse_client(node_server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 调用 Node.js 端的 'search' 工具
                result = await session.call_tool(
                    name="search",
                    arguments={"query": query, "limit": limit}
                )

                # 解析结果
                final_text = ""
                for content in result.content:
                    if content.type == 'text':
                        final_text += content.text
                return final_text

    except Exception as e:
        # 把详细错误打印出来，方便调试
        error_msg = f"搜索服务连接失败: {str(e)}。请检查 Node 服务是否在 localhost:3000 运行。"
        print(error_msg)
        raise e # 抛出异常以便测试脚本捕获

# 负责调用搜索逻辑
@server.tool(name='网络资源搜索')
async def web_search(query: str, limit: int = 3) -> str:
    """MCP 工具入口，专门给 AI 使用"""
    return await search_logic(query, limit)