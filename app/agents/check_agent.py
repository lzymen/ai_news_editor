import json
import re
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState

# 全局计数器：防止死循环
check_retry_counts = {}

prompt = ChatPromptTemplate.from_template("""
你是校对员。请核实内容真实性。
【参考资料】：{search_data}
【待校对内容】：{content}

【判决标准】：
1. **以资料为准**：资料里有的就是真的。
2. **允许常识**：如果资料里没写，但内容符合常识（如人名、职位），**请直接 PASS**。
3. **不要吹毛求疵**：除非有明显的事实冲突，否则优先选择 PASS。

输出 JSON: {{"pass": true/false, "idea": "意见"}}
""")


async def check_agent(state: MessageState):
    print("== 运行 Check Agent (校对) ==")

    content = state.get("write_submit", "")
    search_data = state.get("search", "")

    outlines = state.get("outlines", [])
    current_section = outlines[0] if outlines else "unknown"

    # --- 防死循环逻辑 ---
    retry_key = str(current_section)[:10]
    check_retry_counts[retry_key] = check_retry_counts.get(retry_key, 0) + 1

    # 重写超过 2 次，强制通过
    if check_retry_counts[retry_key] > 2:
        print(f"校对死循环，强制通过。")
        return {
            "check_pass": True,
            "check_idea": "强制通过",
            "who": "comment"
        }
    # -------------------

    chain = prompt | zhipu_llm
    response = await chain.ainvoke({
        "content": content,
        "search_data": search_data
    })

    try:
        cleaned = re.sub(r'```json\s*', '', response.content).replace('```', '').strip()
        data = json.loads(cleaned)
    except:
        data = {"pass": True, "idea": ""}

    is_pass = data.get("pass", False)
    idea = data.get("idea", "需修改")

    print(f"校对结果: {' 通过' if is_pass else ' 驳回'} - {idea}")

    return {
        "check_pass": is_pass,
        "check_idea": idea,
        "who": "check" if not is_pass else "comment"
    }


def check_should_continue(state: MessageState):
    if state.get("check_pass"):
        return "comment_agent"
    else:
        return "write_agent"