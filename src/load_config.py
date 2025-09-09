import os
import yaml
from importlib import resources


class Configloader:
    def __init__(self):
        pass
    
    def load_config_simple(self):
        """개선된 config 로딩 - 표준 경로 지원으로 글로벌 사용 문제 해결"""
        # 1) 환경변수 지정 경로 > 2) 사용자 전역 설정 > 3) 프로젝트별 > 4) 패키지 내 기본값
        if resources.files("src.config").joinpath("config.yaml").exists():
            try:
                text = resources.files("src.config").joinpath("config.yaml").read_text(encoding="utf-8")
                data = yaml.safe_load(text) or {}
                print("✅ 패키지 내 config 사용 (읽기전용)")
                return data
            except Exception:
                print("⚠️ config 없음 (기본값 사용)")
            return {}
        
        else:
            candidates = [
                # === 1순위: 환경변수 (기존 유지) ===
                os.getenv("MCP_CLIENT_CONFIG"),

                # === 2순위: 사용자 전역 설정 (NEW!) ===
                # 이 경로들이 핵심! 글로벌 설치 시 주로 여기서 찾게 됨
                os.path.expanduser("~/.config/mcp-client/config.yaml"),    # XDG 표준 (Linux/macOS)
                os.path.expanduser("~/.config/mcp-client/config.yml"),
                os.path.expanduser("~/.mcp-client/config.yaml"),           # dotfile 스타일
                os.path.expanduser("~/.mcp-client/config.yml"),
                os.path.expanduser("~/.mcp-client.yaml"),                  # 단일 파일 스타일
                os.path.expanduser("~/.mcp-client.yml"),

                # === 3순위: 프로젝트별 설정 (기존 유지) ===  
                "./config.yaml",        # 현재 작업 디렉토리
                "./config.yml",
                "./mcp-client.yaml",    # 명시적 프로젝트 설정
                "./mcp-client.yml",
                "./.mcp-client.yaml",   # 숨김 파일 스타일
                "./.mcp-client.yml",
                ]
            for p in candidates:
                if p and os.path.isfile(p):
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f) or {}
                        print(f"✅ config 로드: {p}")
                        return data
                    except Exception as e:
                        print(f"⚠️ 로컬 config 읽기 실패 {p}: {e}")
                return data
        print("⚠️ config 없음 (기본값 사용)")
        return {}