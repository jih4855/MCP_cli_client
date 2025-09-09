import typer
from src.memory import MemoryManager
from src.load_llm import LLM
from src.mcp_manager import MCPmanager
import yaml
import uuid
from ascii_banner import print_clean_banner, print_minimal_banner
from dotenv import load_dotenv
import os
from importlib import resources  # <= 단일 import

load_dotenv()
Memory = MemoryManager()
app = typer.Typer()
mcp = MCPmanager()

def _load_config_simple():
    # 1) 환경변수 지정 경로 > 2) 현재폴더 config.yaml/yml > 3) 패키지 내 기본값
    candidates = [os.getenv("MCP_CLIENT_CONFIG"), "config.yaml", "config.yml"]
    for p in candidates:
        if p and os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                print(f"✅ config 로드: {p}")
                return data
            except Exception as e:
                print(f"⚠️ 로컬 config 읽기 실패 {p}: {e}")
    # 패키지 fallback (src/config/config.yaml)
    try:
        text = resources.files("src.config").joinpath("config.yaml").read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        print("✅ 패키지 내 config 사용 (읽기전용)")
        return data
    except Exception:
        print("⚠️ config 없음 (기본값 사용)")
        return {}

@app.command()
async def chat():
    print_clean_banner()
    print_minimal_banner()
    print("💡 '끝'을 입력하면 대화가 종료됩니다.\n")

    config = _load_config_simple()

    # MCP 서버 시작
    mcp.load_config()
    await mcp.start_all_servers()

    all_tools = []
    for server_name in mcp.server_configs:
        if server_name not in getattr(mcp, "sessions", {}):
            continue
        try:
            tools = await mcp.get_available_tools(server_name)
            all_tools.extend(tools)
        except Exception as e:
            print(f"[WARN] 툴 조회 실패 {server_name}: {e}")

    print(f"🛠️  총 {len(all_tools)} 도구 로드 완료")
    print(f"🔍 서버 설정: {list(mcp.server_configs.keys())}")
    print(f"🔍 활성 세션: {list(getattr(mcp, 'sessions', {}).keys())}")

    session_id = str(uuid.uuid4())

    llm_instance = LLM(
        model=config.get("model", "gemini-2.5-flash"),
        system_prompt=config.get("system_prompt", ""),
        provider=config.get("provider", ""),
        api_key=os.getenv("api_key", ""),
        api_base=config.get("api_base", None),
        session_id=session_id,
        max_context=config.get("max_context", 20),
        mcp_manager=mcp
    )
    print(f"🧠 LLM 초기화 완료: {llm_instance.model} ({llm_instance.provider})")

    try:
        while True:
            user_input = input("user: ").strip()
            if user_input == "끝":
                print("대화 종료")
                break
            response = await llm_instance.check_provider(user_input, all_tools)
            print(f"assistant: {response}\n")
    finally:
        try:
            await mcp.stop_all_servers()
        except Exception:
            pass
        Memory.close()

def main():
    import asyncio
    asyncio.run(chat())

if __name__ == "__main__":
    main()