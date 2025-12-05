import asyncio
import sys
import os

# 确保能找到 app 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.mcp_server.tools_server import search_logic


async def main():
    keyword = "中华有多少年的历史"
    print(f"🔄 正在测试搜索功能，关键词：{keyword}...")

    try:
        # 调用纯逻辑函数
        result = await search_logic(query=keyword, limit=5)

        print("\n 测试成功！返回结果如下：")
        print("-" * 30)
        print(result)
        print("-" * 30)
    except Exception as e:
        print("测试失败！")
        print(f"错误详情: {e}")


if __name__ == "__main__":
    asyncio.run(main())