```text
 __  __  ____   ____        ____ _     ___       ____ _ _            _ 
|  \/  |/ ___| |  _ \      / ___| |   |_ _|     / ___| (_) ___ _ __ | |_
| |\/| | |     | |_) |    | |   | |    | |     | |   | | |/ _ \ '_ \| __|
| |  | | |___  |  _ <     | |___| |___ | |     | |___| | |  __/ | | | |_ 
|_|  |_|\____| |_| \_\     \____|_____|___|     \____|_|_|\___|_| |_|\__|
```

# MCP CLI Client

CLI 환경에서 MCP(Model Context Protocol) server를 활용할 수 있는 다중 LLM 지원 client입니다.

## 📖 문서 사이트
- **[한국어 문서](https://jih4855.github.io/MCP_cli_client/)**
- **[English Documentation](https://jih4855.github.io/MCP_cli_client/index-en.html)**

> GitHub Pages로 호스팅되는 대화형 문서 사이트에서 설치부터 사용법까지 모든 내용을 확인할 수 있습니다.

## 🎯 프로젝트 목적

Ubuntu/Linux 환경에서 MCP server와 연동하여 다양한 시스템 도구를 활용할 수 있는 CLI 기반 AI assistant를 제공합니다.

## ✨ 주요 기능

- 🤖 **다중 LLM 지원**: Gemini (완전 지원), Ollama, OpenAI (기본 지원)
- 🔗 **MCP server 연동**: 여러 MCP server와 병렬 연결 및 도구 실행
- 🐧 **Ubuntu 시스템 도구**: 시스템 정보, 메모리, CPU, 네트워크 모니터링
- 💾 **대화 기록 관리**: SQLite 기반 session별 대화 저장
- ⚡ **비동기 처리**: 빠른 응답을 위한 병렬 도구 실행
- 🛠️ **확장 가능한 구조**: 새로운 LLM provider 및 MCP server 쉽게 추가

## 📋 지원 상태

| 기능 | 상태 | 설명 |
|------|------|------|
| **Gemini LLM** | ✅ 완료 | 다중 도구 병렬 실행, Function Calling 지원 |
| **Ubuntu MCP Server** | ✅ 완료 | 시스템 정보, 메모리, CPU, 프로세스 모니터링 |
| **Ollama LLM** | 🚧 개발중 | 기본 채팅만 지원 |
| **OpenAI LLM** | 🚧 개발중 | 기본 채팅만 지원 |
| **글로벌 설치** | ✅ 완료 | `pip install -e .`로 어디서든 `mcp-client` 실행 |

## 🚀 빠른 시작

### 글로벌 설치 (권장)

1. **저장소 클론**
```bash
git clone https://github.com/jih4855/MCP_cli_client.git
cd MCP_cli_client
```

2. **가상환경 설정 및 설치**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install -e .
```

3. **어디서든 실행**
```bash
mcp-client  # 가상환경 활성화 없이 실행 가능
```

### 개발 모드 설치

1. **저장소 클론 및 가상환경**
```bash
git clone https://github.com/jih4855/MCP_cli_client.git
cd MCP_cli_client
python -m venv venv
source venv/bin/activate
```

2. **의존성만 설치**
```bash
pip install -r requirements.txt
```

3. **개발 모드 실행**
```bash
python main.py  # 가상환경 활성화 필요
```

### 설정

1. **환경변수 설정** (`.env` 파일 생성)
```env
api_key=your_gemini_api_key_here
```

2. **LLM 설정** (`config.yaml`)
```yaml
system_prompt: |
  당신은 도움이 되는 AI assistant입니다.
  
model: gemini-2.5-flash
provider: gemini  
api_base: None
max_context: 20
session_id: "default"
```

3. **MCP server 설정** (`mcp_config.json`)
```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "python",
      "args": ["/path/to/your/mcp_server.py"],
      "description": "server 설명"
    }
  }
}
```

### 실행

#### 글로벌 설치 후
```bash
mcp-client  # 어디서든 실행
```

#### 개발 모드
```bash
source venv/bin/activate  # 가상환경 활성화
python main.py           # 직접 실행
```

## 💡 사용 예시

```bash
$ mcp-client
💡 '끝'을 입력하면 대화가 종료됩니다.

✅ config.yaml 로드 완료
🛠️  총 8개 도구 로드 완료
🔍 서버 설정: ['ubuntu-info']
🧠 LLM 초기화 완료: gemini-2.5-flash (gemini)

user: 현재 시간과 시스템 정보 알려줘
🔍 도구 호출: get_current_time
🔍 도구 호출: get_ubuntu_system_info
✅ 도구 실행 완료
assistant: 현재 시간은 2025년 1월 9일이고, Ubuntu 22.04 시스템에서 실행 중입니다. 
커널 버전은 5.15.0이며, 시스템 업타임은 2일 14시간입니다.

user: 끝
대화 종료
```

## 📁 프로젝트 구조

```
typer_cli/
├── main.py                 # CLI 진입점
├── src/
│   ├── load_llm.py         # LLM provider 관리 (Gemini, Ollama, OpenAI)
│   ├── mcp_manager.py      # MCP server 연결 및 도구 실행
│   └── memory.py           # SQLite 기반 대화 기록 관리
├── mcp_server/            
│   └── MCP_official.py     # Ubuntu 시스템 정보 MCP server
├── docs/                   # GitHub Pages 문서
│   ├── index.html          # 한국어 문서
│   ├── index-en.html       # 영문 문서
│   ├── styles.css          # 스타일시트
│   └── script.js           # 인터랙티브 기능
├── tests/                  # 테스트 코드
├── config.yaml            # LLM 설정
├── mcp_config.json        # MCP server 설정
├── pyproject.toml         # 패키지 설정 (글로벌 설치용)
├── requirements.txt       # Python 의존성
└── .env                   # API 키 (Git 제외)
```

## 🔧 설정 가이드

### MCP server 추가

```json
{
  "mcpServers": {
    "ubuntu-info": {
      "command": "python",
      "args": ["mcp_server/MCP_official.py"],
      "description": "Ubuntu 시스템 정보 조회"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem@latest", "/home"],
      "description": "파일시스템 접근"
    },
    "git": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-git@latest", "--repository", "/path/to/repo"],
      "description": "Git 저장소 관리"
    }
  }
}
```

## 📖 사용법

### 기본 대화

```
user: 안녕하세요!
assistant: 안녕하세요! 무엇을 도와드릴까요?

user: 끝
대화 종료
```

### 도구 사용 예시

```
user: 현재 시간과 시스템 정보를 알려주세요
🔍 도구 호출: get_current_time
🔍 도구 호출: get_ubuntu_system_info  
✅ 도구 실행 완료
assistant: 현재 시간은 2025년 1월 9일이고, Ubuntu 22.04 LTS 시스템에서 실행 중입니다.

user: 메모리 사용량 확인해줘
🔍 도구 호출: get_ubuntu_memory_info
✅ 도구 실행 완료
assistant: 총 메모리 8GB 중 4.2GB 사용 중이고, 3.8GB가 사용 가능합니다.
```

## 🏗️ Architecture

### 핵심 Component

- **LLM class**: 다중 LLM provider 추상화 (Gemini, Ollama, OpenAI)
- **MCPmanager**: MCP server 연결 및 도구 실행 관리
- **MemoryManager**: SQLite 기반 대화 기록 저장
- **Ubuntu MCP Server**: 시스템 모니터링 도구 제공

### 비동기 처리 흐름

1. **MCP Server 시작**: 모든 설정된 서버와 병렬 연결
2. **도구 수집**: 각 서버에서 사용 가능한 도구 목록 수집
3. **LLM 초기화**: 선택된 provider로 LLM 인스턴스 생성
4. **사용자 입력 처리**: Function Calling으로 필요한 도구 결정
5. **병렬 도구 실행**: 선택된 도구들을 동시에 실행
6. **결과 통합**: 모든 결과를 통합하여 자연어 응답 생성

### Ubuntu MCP Server 도구

- `get_ubuntu_system_info`: OS 정보, 커널, 업타임
- `get_ubuntu_memory_info`: 메모리 사용량 (`free -h`)
- `get_ubuntu_cpu_info`: CPU 정보 (`lscpu`)
- `get_ubuntu_disk_info`: 디스크 사용량 (`df -h`)
- `get_ubuntu_process_info`: 상위 CPU 사용 프로세스
- `get_ubuntu_network_info`: 네트워크 인터페이스 정보

## 🧪 Test

```bash
# 기본 test 실행
python -m pytest tests/

# MCP 연결 test
python tests/test_mcp_module.py

# Gemini 연동 test  
python tests/test_gemini.py
```

## 🤝 기여하기

1. Fork 후 branch 생성
2. 기능 개발 또는 bug 수정
3. Test code 작성
4. PR 생성

### 개발 우선순위

- [ ] OpenAI Function Calling 완성
- [ ] Ollama Function Calling 구현  
- [ ] 더 많은 Ubuntu 도구 추가 (패키지 관리, 로그 분석 등)
- [ ] CLI 명령어 옵션 확장 (Typer 활용)
- [ ] Web UI 개발 (선택사항)

## 🐛 알려진 이슈

- OpenAI, Ollama에서 Function Calling 미완성
- 일부 Ubuntu 명령어에서 권한 문제 가능 
- 대용량 시스템 정보 출력 시 응답 지연 가능
- 네트워크 연결이 불안정할 때 MCP 서버 재연결 필요

## 📦 설치 방법 요약

| 방법 | 장점 | 단점 |
|------|------|------|
| **글로벌 설치** | 어디서든 `mcp-client` 실행 | 시스템 Python에 설치 |
| **개발 모드** | 코드 수정 즉시 반영 | 가상환경 활성화 필요 |
| **pipx 설치** | 격리된 환경 + 글로벌 명령어 | pipx 별도 설치 필요 |

### pipx 설치 (권장)
```bash
# pipx 설치 (한 번만)
pip install pipx
pipx install .

# 실행
mcp-client  # 격리된 환경에서 실행
```

## 📄 License

오픈소스 프로젝트입니다.

## 🔗 관련 링크

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Anthropic MCP 가이드](https://github.com/modelcontextprotocol)
- [MCP server 목록](https://github.com/modelcontextprotocol/servers)

---

⭐ **Gemini LLM + Ubuntu MCP Server 완전 지원**
- Function Calling을 통한 다중 도구 병렬 실행
- 실시간 시스템 모니터링 및 정보 조회
- 글로벌 설치로 어디서든 실행 가능

🚧 **개발 진행 중**
- OpenAI, Ollama Function Calling 구현
- 더 많은 시스템 도구 및 MCP 서버 추가