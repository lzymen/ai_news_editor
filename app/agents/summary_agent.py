from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState

prompt = ChatPromptTemplate.from_template("""
你是主编。请根据以下所有段落，整理成一篇完整的新闻稿。
进行最后的排版润色，不要改变原意。

【文章标题】：{title}
【所有段落】：{paragraphs}
""")


async def summary_agent(state: MessageState):
    print("== 运行 Summary Agent (最终排版) ==")

    title = state.get("title", "")
    paragraphs = state.get("paragraphs", [])

    chain = prompt | zhipu_llm
    response = await chain.ainvoke({
        "title": title,
        "paragraphs": "\n\n".join(paragraphs)
    })

    final_article = response.content
    print("文章生成完毕！")

    # 将最终结果存入 search 字段或者单独的 result 字段方便查看
    return {
        "search": final_article
    }