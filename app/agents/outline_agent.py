import json
import re
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState

prompt = ChatPromptTemplate.from_template("""
你负责新闻大纲编写。
请综合【标题】和【搜索资料】，编写一个清晰的新闻大纲。

【标题】：{title}

【搜索资料】：
{search_data}

【要求】：
1. 结构必须清晰，包含一级标题和二级标题。
2. 内容必须基于搜索资料，不能瞎编。
3. **严格输出 JSON 格式**，不要包含 Markdown 标记（如 ```json ... ```）。
4. JSON 格式必须包含 "title" (总标题) 和 "sections" (段落列表，每个元素是一个简短的段落标题)。

【示例格式】：
{{
    "title": "新闻标题",
    "sections": ["第一段：背景介绍", "第二段：核心事件", "第三段：影响分析", "第四段：未来展望"]
}}
""")


async def outline_agent(state: MessageState):
    print('==' * 5 + ' 运行 Outline Agent (大纲生成) ' + '==' * 5)

    # 1. 获取输入
    title = state.get('title', state.get('topic', ''))
    search_data = state.get('search', '无搜索资料')


    # 2. 调用模型
    chain = prompt | zhipu_llm
    response = await chain.ainvoke({
        "title": title,
        "search_data": search_data
    })

    content = response.content
    print(f"大纲生成原始内容: {content[:50]}...")

    # 3. 解析 JSON (这是核心，防止模型输出 markdown 格式)
    try:
        # 尝试清理 markdown 符号
        cleaned_content = re.sub(r'```json\s*', '', content).replace('```', '').strip()
        data = json.loads(cleaned_content)

        # 提取 sections
        outlines = data.get("sections", [])
        print(outlines)

    except Exception as e:
        print(f" JSON 解析失败，尝试回退策略: {e}")
        # 如果解析失败，简单按行分割作为大纲
        outlines = [line for line in content.split('\n') if line.strip()]

    print(f"大纲解析成功，共 {len(outlines)} 个章节")

    # 4. 返回结果
    return {
        "outlines": outlines
    }