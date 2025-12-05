import json
import re
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState

# 全局计数器
comment_retry_counts = {}

prompt = ChatPromptTemplate.from_template("""
你是评论员。请评价稿件质量。
【当前大纲】：{outline}
【待评内容】：{content}
【资料概况】：{search_summary}

【审核标准】：
1. **必须通过**：语句通顺、符合大纲即可。
2. **资料不足时**：如果【资料概况】显示资料很少，请降低标准，**不要**因为内容空洞而驳回。
3. 只有出现严重语病或逻辑混乱才驳回。

输出 JSON: {{"pass": true/false, "idea": "意见"}}
""")


async def comment_agent(state: MessageState):
    print("== 运行 Comment Agent (审核) ==")

    content = state.get("write_submit", "")
    outlines = state.get("outlines", [])
    current_section = outlines[0] if outlines else "unknown"
    search_data = state.get("search", "")
    search_summary = f"资料长度 {len(search_data)} 字" if search_data else "无资料"

    # --- 防死循环逻辑 ---
    retry_key = str(current_section)[:10]
    comment_retry_counts[retry_key] = comment_retry_counts.get(retry_key, 0) + 1

    if comment_retry_counts[retry_key] > 3:
        print(f"评论死循环，强制通过。")
        # 强制归档
        paragraphs = state.get("paragraphs", [])
        paragraphs.append(content)
        if outlines: del outlines[0]

        return {
            "paragraphs": paragraphs,
            "outlines": outlines,
            "comment_pass": True,
            "who": "outline"
        }
    # -------------------

    chain = prompt | zhipu_llm
    response = await chain.ainvoke({
        "outline": current_section,
        "content": content,
        "search_summary": search_summary
    })

    try:
        cleaned = re.sub(r'```json\s*', '', response.content).replace('```', '').strip()
        data = json.loads(cleaned)
    except:
        data = {"pass": True, "idea": ""}

    is_pass = data.get("pass", False)
    idea = data.get("idea", "")

    paragraphs = state.get("paragraphs", [])
    next_who = "comment"

    if is_pass:
        print(" 评论通过")
        paragraphs.append(content)
        if outlines: del outlines[0]
        next_who = "outline"
    else:
        print(f" 评论驳回: {idea}")
        next_who = "comment"

    return {
        "paragraphs": paragraphs,
        "outlines": outlines,
        "comment_idea": idea,
        "who": next_who,
        "comment_pass": is_pass
    }


def comment_should_continue(state: MessageState):
    if state.get("comment_pass"):
        if not state.get("outlines"):
            return "summary_agent"
        else:
            return "write_agent"
    else:
        return "write_agent"