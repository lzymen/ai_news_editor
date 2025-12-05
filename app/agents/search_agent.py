from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState
from app.core.config import python_mcp_server_config
from langchain_mcp_adapters.client import MultiServerMCPClient

# 初始化 MCP 客户端
mcp_client = MultiServerMCPClient({'python_mcp': python_mcp_server_config})

# --- 核心修改：Prompt 优化，强制提取关键词 ---
prompt = ChatPromptTemplate.from_template("""
你是一个专业的新闻搜索员。
你的任务是为标题“{title}”搜索最相关的背景资料。

【严重警告】：
1. **不要**直接把标题当作搜索词，搜索引擎可能听不懂。
2. **必须**提取标题中的核心实体（人名、地名、事件）作为关键词。
3. 如果标题包含生僻词或修辞（如“激辩”、“风云”），请去掉它们，只保留核心事件。

【正确示例】：
标题：特朗普及拜登在摇摆州激战
搜索词：特朗普 拜登 摇摆州 选举 2024

【当前标题】：{title}
【已知信息】：{existing_info}

【指令】：
- 如果【已知信息】不足（少于50字），请调用搜索工具。
- 搜索时，请构造一个由空格分隔的关键词组合（例如：高市早苗 台湾 言论）。
- 如果【已知信息】已足够，请直接输出摘要。
""")


async def search_agent(state: MessageState):
    print('==' * 5 + ' 运行 Search Agent ' + '==' * 5)

    title = state.get('title', state.get('topic'))
    existing_search = state.get("search", "")

    # 1. 检查已有资料
    if existing_search and len(str(existing_search)) > 50:
        print(f" [Search Agent] 复查已有资料 ({len(existing_search)}字)，跳过搜索。")
        return {
            "response": None,
            "search": existing_search
        }

    # 2. 准备搜索
    print(f" [Search Agent] 正在为 '{title}' 规划搜索词...")
    mcp_tools = await mcp_client.get_tools()
    model_with_tools = zhipu_llm.bind_tools(mcp_tools)

    chain = prompt | model_with_tools
    response = await chain.ainvoke({
        "title": title,
        "existing_info": existing_search if existing_search else "暂无"
    })

    if response.tool_calls:
        #方便调试
        for tool_call in response.tool_calls:
            print(f"[Search Agent] 决定搜索: {tool_call['args']}")
        return {"response": response}
    else:
        print("[Search Agent] 输出搜索结果摘要。")
        return {
            "response": response,
            "search": response.content
        }


def search_should_continue(state: MessageState):
    response = state.get("response")
    if response and response.tool_calls:
        return "tools"
    return "outline_agent"