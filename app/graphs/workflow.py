import asyncio
from langgraph.graph import StateGraph, END
from app.graphs.state import MessageState

from app.agents.title_agent import title_agent
from app.agents.search_agent import search_agent, search_should_continue
from app.agents.outline_agent import outline_agent
from app.agents.write_agent import write_agent
from app.agents.check_agent import check_agent, check_should_continue
from app.agents.comment_agent import comment_agent, comment_should_continue
from app.agents.summary_agent import summary_agent

# 2. 导入工具执行逻辑
from app.mcp_server.tools_server import search_logic


# --- 自定义工具节点 ---
# app/graphs/workflow.py 中的 call_tool_node

async def call_tool_node(state: MessageState):
    response = state.get("response")
    tool_calls = response.tool_calls
    final_result = ""

    for call in tool_calls:
        if call["name"] in ["网络资源搜索", "search", "web_search"]:
            query = call["args"].get("query")
            print(f" [Tools] 正在执行搜索: {query}")  # <--- 这里的打印很重要

            try:
                result = await search_logic(query=query)
                # 打印搜到的前50个字，确认不是“汉字解释”
                preview = str(result).strip()[:50].replace('\n', ' ')
                print(f" 搜索结果预览: {preview}...")

                final_result += f"{str(result)}\n\n"
            except Exception as e:
                final_result += f"Error: {e}\n"

    return {"search": final_result}


# --- 构建工作流 ---
def create_graph():
    workflow = StateGraph(MessageState)

    # 1. 注册所有节点
    workflow.add_node("title_agent", title_agent)
    workflow.add_node("search_agent", search_agent)
    workflow.add_node("tools", call_tool_node)
    workflow.add_node("outline_agent", outline_agent)
    workflow.add_node("write_agent", write_agent)
    workflow.add_node("check_agent", check_agent)
    workflow.add_node("comment_agent", comment_agent)
    workflow.add_node("summary_agent", summary_agent)

    # 2. 设置入口
    workflow.set_entry_point("title_agent")

    # 3. 连接节点 (配置流水线)

    # 标题 -> 搜索
    workflow.add_edge("title_agent", "search_agent")

    # 搜索 -> (判断) -> 工具 或 大纲
    workflow.add_conditional_edges(
        "search_agent",
        search_should_continue,
        {
            "tools": "tools",
            "outline_agent": "outline_agent"
        }
    )
    # 工具 -> 回搜索 (循环)
    workflow.add_edge("tools", "search_agent")

    # 大纲 -> 写稿
    workflow.add_edge("outline_agent", "write_agent")

    # 写稿 -> 校对
    workflow.add_edge("write_agent", "check_agent")

    # 校对 -> (判断) -> 评论 或 重写
    workflow.add_conditional_edges(
        "check_agent",
        check_should_continue,
        {
            "comment_agent": "comment_agent",  # 通过 -> 去评论
            "write_agent": "write_agent"  # 不通过 -> 回去重写
        }
    )

    # 评论 -> (判断) -> 总结 或 写下一段
    workflow.add_conditional_edges(
        "comment_agent",
        comment_should_continue,
        {
            "summary_agent": "summary_agent",  # 大纲空了 -> 去总结
            "write_agent": "write_agent"  # 还有大纲 -> 写下一段
        }
    )

    # 总结 -> 结束
    workflow.add_edge("summary_agent", END)

    return workflow.compile()



if __name__ == "__main__":
    async def main():
        app = create_graph()

        # 初始输入
        initial_input = {"topic": "饿了么更名淘宝闪购！"}

        async for event in app.astream(initial_input):
            for node_name, state_update in event.items():
                print(f"[{node_name}] 执行完成")

                # 打印一些关键产出，方便观察进度
                if not state_update:
                    continue

                if "search" in state_update and len(state_update["search"]) > 50:
                    print(f"    已获取资料: {len(state_update['search'])} 字")

                if "outlines" in state_update and isinstance(state_update["outlines"], list):
                    print(f"   大纲剩余章节: {len(state_update['outlines'])}")

                if "write_submit" in state_update:
                    print(f"   当前草稿片段: {state_update['write_submit'][:30]}...")

                # 最终成果
                if node_name == "summary_agent" and "search" in state_update:
                    print("【最终成稿】")
                    print(state_update["search"])  # 这里借用 search 字段或者你自己定义的字段


    asyncio.run(main())