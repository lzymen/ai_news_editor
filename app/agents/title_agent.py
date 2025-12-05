
from app.core.llm import zhipu_llm
from app.graphs.state import MessageState
from langchain_core.prompts import ChatPromptTemplate

"""
根据用户的输入的话题或者问题，
生成更符合新闻领域的标题。
"""

prompt = ChatPromptTemplate.from_template("""
你是一名资深新闻编辑，擅长撰写吸引眼球且符合新闻规范的标题。
请基于以下原始标题：{topic}，重新创作一个更具吸引力、简洁有力且符合新闻规范的标题。
要求：
1. 不超过20个字
2. 语言简洁、有冲击力
3. 符合新闻标题的表达习惯
4. 仅输出标题，不要有任何解释或多余内容
""")

def title_agent(state: MessageState):
    print('=='*5+'现在正在运行title_agent'+'=='*5)
    # 1.接受参数
    topic = state['topic']
    model = zhipu_llm
    paragraphs = []

    # 2.agent调用
    chain = prompt | model
    resp = chain.invoke({'topic':topic})
    new_tittle = resp.content
    print(new_tittle)
    paragraphs.append(new_tittle)
    return {
        'title':new_tittle,
        'paragraphs':paragraphs,
        'search': ""
    }

if __name__ == '__main__':
    state = MessageState(topic ='2024年的诺贝尔奖得主')
    title_agent(state)


