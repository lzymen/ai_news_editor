# app/api/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.schemas.news import NewsRequest, NewsResponse
from app.graphs.workflow import create_graph
import json
import asyncio

router = APIRouter()

# 初始化图（Graph），避免每次请求都重新编译
news_graph = create_graph()


@router.post("/generate", response_model=NewsResponse, summary="生成完整新闻 (等待模式)")
async def generate_news(request: NewsRequest):
    """
    触发新闻生成工作流，等待所有步骤完成后返回最终结果。
    """
    try:
        initial_input = {"topic": request.request.topic}
        # 修正：直接使用 request.topic
        inputs = {"topic": request.topic}

        final_state = await news_graph.ainvoke(inputs)

        # 从最终状态中提取数据 (根据 summary_agent 的返回逻辑)
        return NewsResponse(
            title=final_state.get("title", "未命名"),
            article=final_state.get("search", "生成失败或无内容"),
            outlines=final_state.get("outlines", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"新闻生成失败: {str(e)}")


@router.post("/generate/stream", summary="生成完整新闻 (流式模式)")
async def stream_news(request: NewsRequest):
    """
    SSE (Server-Sent Events) 风格的流式输出。
    实时返回 Agent 的执行步骤和中间结果。
    """

    async def event_generator():
        inputs = {"topic": request.topic}
        try:

            async for event in news_graph.astream(inputs):
                for node_name, state_update in event.items():
                    # 构造要发送给前端的消息
                    data = {
                        "node": node_name,
                        "update": str(state_update)[:200] + "..."
                    }

                    # 特殊处理：如果已经写好了某一段，可以专门把那一段推出去
                    if "write_submit" in state_update:
                        data["draft_fragment"] = state_update["write_submit"]

                    # 最终结果检测
                    if node_name == "summary_agent" and "search" in state_update:
                        data["final_article"] = state_update["search"]

                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")