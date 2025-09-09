import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.load_llm import LLM
import yaml
import asyncio
import dotenv

dotenv.load_dotenv()
# config.yaml 파일에서 설정 읽기
try:
    with open("config.yaml", "r", encoding="utf-8") as f:
        config_path = yaml.safe_load(f)
        if config_path is None:
            print("config 파일이 비어 있습니다.")
        else:
            print(f"✅ config.yaml 로드 완료")
except FileNotFoundError:
    print("config.yaml 파일을 찾을 수 없습니다.")


gemini = LLM(model = config_path.get("gemini", {}).get("model", "gemini-2.5-flash"),
                   system_prompt = config_path.get("system_prompt", ""),
                   provider = config_path.get("gemini", {}).get("provider", ""),
                   api_key = os.getenv("api_key", "")
            )

async def main():
    response = await gemini.chat_gemini("안녕?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())

# def test_feedback_roof(feedback = True)
    
