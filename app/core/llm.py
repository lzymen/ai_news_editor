from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core.env_utils import ZHIPU_API_KEY,ZHIPU_BASE_URL,QIANWEN_API_KEY,QIANWEN_BASE_URL


zhipu_llm = ChatOpenAI(
    model = "glm-4-plus",
    temperature= 0.7,
    api_key = ZHIPU_API_KEY,
    base_url=ZHIPU_BASE_URL
)

qianwen_llm = ChatOpenAI(
    model = "qwen-flash",
    temperature= 0.7,
    api_key = QIANWEN_API_KEY,
    base_url= QIANWEN_BASE_URL
)

if __name__ == '__main__':
    # resp = zhipu_LLM.invoke([HumanMessage(content="你是谁，你能帮我解决问题吗")])
    # print(resp.content)

    resp = zhipu_llm.invoke([HumanMessage(content="你是谁，你能帮我解决问题吗")])
    print(resp.content)

