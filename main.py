import typer
from src.memory import MemoryManager
from src.load_llm import LLM
from src.mcp_manager import MCPmanager
import yaml
import uuid
from ascii_banner import print_clean_banner, print_minimal_banner
from dotenv import load_dotenv
import os

load_dotenv()
Memory = MemoryManager()
app = typer.Typer()
mcp = MCPmanager()


@app.command()
async def chat():
    print_clean_banner()
    print_minimal_banner()
    print("💡 '끝'을 입력하면 대화가 종료됩니다.\n")
    # config.yaml 파일에서 system_prompt 읽기 및 LLM 초기화
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config is None:
                print("config 파일이 비어 있습니다.")
            else:
                print(f"✅ config.yaml 로드 완료")
    except FileNotFoundError:
        print("config.yaml 파일을 찾을 수 없습니다. 파일을 생성하고 설정을 추가하세요.")
        return 

    except yaml.YAMLError as e:
        print(f"YAML 파싱 오류: {e}")
        return
    
    # MCP 서버 시작
    mcp.load_config()
    
    await mcp.start_all_servers()
    
    all_tools = []
    
    for server_name in mcp.server_configs:
        tools = await mcp.get_available_tools(server_name)
        all_tools.extend(tools)
    print(f"🛠️  총 {len(all_tools)} 도구 로드 완료")
    print(f"🔍 서버 설정: {list(mcp.server_configs.keys())}")
    print(f"🔍 활성 세션: {list(mcp.sessions.keys()) if hasattr(mcp, 'sessions') else '없음'}")

    session_id = str(uuid.uuid4())  # 세션 ID 생성

    llm_instance = LLM(model=config.get("model", "gemini-2.5-flash"),
                       system_prompt=config.get("system_prompt", ""),
                       provider=config.get("provider", ""),
                       api_key=os.getenv("api_key", ""),
                       api_base=config.get("api_base", ""),
                       session_id=session_id,
                       max_context=config.get("max_context", 20),
                       mcp_manager=mcp)
    print(f"🧠 LLM 초기화 완료: {llm_instance.model} ({llm_instance.provider})")
    
    try:
        while True:
            user_input = input("user: ")
            if user_input == "끝":
                print("대화 종료")
                break
            
            response = await llm_instance.check_provider(user_input, all_tools)

            print(f"assistant: {response}\n")

    finally:
        try:
            # MCP 서버가 있다면 정리 종료
            await mcp.stop_all_servers()
        except Exception:
            pass
        Memory.close()

def main():
    """CLI 진입점"""
    import asyncio
    asyncio.run(chat())

if __name__ == "__main__":
    main()