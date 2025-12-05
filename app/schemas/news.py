
from pydantic import BaseModel, Field
from typing import List, Optional

class NewsRequest(BaseModel):
    topic: str = Field(..., description="新闻的话题或原始标题", example="2024年诺贝尔奖揭晓")

class NewsResponse(BaseModel):
    title: str = Field(..., description="最终生成的标题")
    article: str = Field(..., description="最终生成的文章内容")
    outlines: Optional[List[str]] = Field(None, description="生成的文章大纲")
    # 可以根据需要添加更多字段