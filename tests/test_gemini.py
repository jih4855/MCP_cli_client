from load_llm import LLM
import os
import yaml

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

llm = LLM(model=config_path.get("gemini", {}).get("model", "gemini-2.5-flash"),
           system_prompt=config_path.get("system_prompt", ""),
           provider=config_path.get("gemini", {}).get("provider", ""),
           api_key=config_path.get("gemini", {}).get("api_key", ""),
           api_base=config_path.get("gemini", {}).get("api_base", ""),
           session_id=config_path.get("gemini", {}).get("session_id", ""),
           max_context=config_path.get("gemini", {}).get("max_context", 20))

response = llm.chat_gemini("안녕?")
print(response)