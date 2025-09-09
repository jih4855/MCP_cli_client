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
            # 1순위: 환경변수
            os.getenv("MCP_CLIENT_CONFIG"),

            # 2순위: XDG 표준 (절대경로)
            os.path.expanduser("~/.config/mcp-client/config.yaml"),
            os.path.expanduser("~/.mcp-client/config.yaml"),

            # 3순위: 홈 디렉토리 직접
            os.path.expanduser("~/config.yaml"),

            # 4순위: 상대경로 (마지막에만)
            "./config.yaml" if os.getcwd().endswith('typer_cli') else None,
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