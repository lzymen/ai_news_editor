# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as news_router
import uvicorn

# 1. 初始化 FastAPI 应用
app = FastAPI(
    title="AI News Editor API",
    description="基于 LangGraph 的多智能体新闻编辑部服务",
    version="1.0.0"
)

# 2. 配置跨域 (CORS) - 允许前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 注册路由
app.include_router(news_router, prefix="/api/v1/news", tags=["News"])

@app.get("/")
async def root():
    return {"message": "欢迎来到 AI 新闻编辑部 API，请访问 /docs 查看文档"}

# 4. 调试启动入口
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)