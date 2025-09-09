import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.mcp_manager import MCPmanager
import asyncio

async def test_basic():
    """기본 서버 시작 테스트"""
    print("=== 1단계: 기본 서버 시작 테스트 ===")
    mcp = MCPmanager()
    mcp.load_config()
    await mcp.start_all_servers()
    print("기본 테스트 완료!\n")
    return mcp

async def main():
    mcp = await test_basic()

if __name__ == "__main__":
    asyncio.run(main())