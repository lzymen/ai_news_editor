from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState

# --- Prompt 1: 根据大纲写 ---
prompt_from_outline = ChatPromptTemplate.from_template("""
你是一名记者。请根据【标题】、【大纲】和【参考资料】撰写段落。

【标题】：{title}
【本段大纲】：{outline}
【参考资料】：
{search_data}

【写作策略】：
1. 有资料时：充分引用数据、言论和细节。
2. 无资料时：保持克制**，用简练、客观的语言概括常识，**绝对不要**堆砌空洞的形容词（如“备受关注”、“引发热议”）。
3. 字数控制在 150 字以内。
""")

# --- Prompt 2: 根据校对修改 ---
prompt_from_check = ChatPromptTemplate.from_template("""
你负责根据校对意见修改段落。
【参考资料】：{search_data}
【原稿】：{content}
【校对意见】：{ideas}

要求：修正事实错误。如果校对说“资料不足”，请尝试从【参考资料】中挖掘细节，或者删除无法被证实的内容，不要硬编。
""")

# --- Prompt 3: 根据评论修改 ---
prompt_from_comment = ChatPromptTemplate.from_template("""
你负责根据评论意见润色段落。
【参考资料】：{search_data}
【原稿】：{content}
【评论意见】：{ideas}

要求：如果评论嫌内容空洞，请尝试引用【参考资料】中的具体人名、地名、时间来增加真实感。
""")


async def write_agent(state: MessageState):
    print('==' * 5 + ' 运行 Write Agent (写作) ' + '==' * 5)

    who = state.get("who", "outline")
    title = state.get("title", "")
    outlines = state.get("outlines", [])
    current_draft = state.get("write_submit", "")
    # 核心：获取搜索资料
    search_data = state.get("search", "无资料")

    if not outlines:
        return {"write_submit": "无大纲"}

    current_section = outlines[0]
    print(f"当前任务: [{who}] - 章节: {current_section}")

    chain = None
    input_data = {}

    if who == "outline":
        chain = prompt_from_outline | zhipu_llm
        input_data = {
            "title": title,
            "outline": current_section,
            "search_data": search_data
        }

    elif who == "check":
        check_idea = state.get("check_idea", "无意见")
        chain = prompt_from_check | zhipu_llm
        input_data = {
            "content": current_draft,
            "ideas": check_idea,
            "search_data": search_data
        }

    elif who == "comment":
        comment_idea = state.get("comment_idea", "无意见")
        chain = prompt_from_comment | zhipu_llm
        input_data = {
            "content": current_draft,
            "ideas": comment_idea,
            "search_data": search_data
        }

    if chain:
        response = await chain.ainvoke(input_data)
        write_submit = response.content
    else:
        write_submit = "Error"

    print(f"产出内容: {write_submit[:50]}...")

    return {
        "write_submit": write_submit,
        "title": title
    }