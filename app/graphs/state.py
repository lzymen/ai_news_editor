"""
state
1.主要存放整个聊天历史记录或者完成需求自定义的数据类型存储的数据
2.每个节点的输入值都默认有这个状态，状态的数据可以从任意的节点中获取
3.所有节点返回的内容目的都是为了更新状态，通过reducer函数来判断怎么影响这个状态的进行。
messagestate------存在与工作流中              agentstate-----------存在于智能体。
"""
from typing import List,TypedDict
class MessageState(TypedDict):
    topic:str # 用户传递进来的问题
    paragraphs:list[str] # [标题, 第一段导语, 第二段正文, 第三段正文...]
    title : str # 模型输出的标题
    search : str # 网络上搜索的资源。
    response : str  # 判断agent传回中是否要使用工具。
    outlines : list # 大纲
    who: str  # 身份识别
    write_submit: str  # 编撰者当前提交的信息内容
    check_idea: object  # 校对意见
    comment_idea: object  # 评论意见
    check_pass: bool  # 检查通过
    comment_pass: bool  # 评论通过