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
- 🎨 **개선된 CLI**: Rich 스타일링 + readline 히스토리

## 📋 지원 상태

| 기능 | 상태 | 설명 |
|------|------|------|
| **Gemini LLM** | ✅ 완료 | MCP 도구 병렬 실행 지원 |
| **Ubuntu MCP Server** | ✅ 완료 | 시스템 정보, 메모리, CPU, 프로세스 모니터링 |
| **Ollama LLM** | 🚧 개발중 | 기본 채팅만 지원 |
| **OpenAI LLM** | 🚧 개발중 | 기본 채팅만 지원 |
| **글로벌 설치** | ✅ 완료 | `pip install -e .`로 어디서든 `mcp-client` 실행 |

## 🚀 빠른 시작

### pipx 설치 (권장)

**모든 환경에서 안정적이고 격리된 설치 방법입니다.**

#### Ubuntu/Debian
```bash
# pipx 설치
sudo apt update && sudo apt install pipx
pipx ensurepath

# 프로젝트 설치
pipx install git+https://github.com/jih4855/MCP_cli_client.git

# MCP 서버 파일 준비 (중요!)
git clone https://github.com/jih4855/MCP_cli_client.git ~/mcp-project

# 설정 파일 복사 및 생성
cp ~/mcp-project/src/config/config.yaml ~/config.yaml 2>/dev/null || cat > ~/config.yaml << 'EOF'
system_prompt: |
  당신은 도움이 되는 AI assistant입니다.
  
model: gemini-2.5-flash
provider: gemini  
api_base: None
max_context: 20
session_id: "default"
EOF

# API 키 설정
cat > ~/.env << 'EOF'
api_key=your_gemini_api_key_here
EOF

# MCP 설정 수정 (UPDATE_THIS_PATH를 실제 경로로)
sed -i 's|UPDATE_THIS_PATH|/home/'$(whoami)'/mcp-project|g' ~/mcp-project/src/config/mcp_config.json

# 어디서든 실행
mcp-client
```

**⚡ PATH 문제 해결**:
```bash
# 새 터미널 열거나
source ~/.bashrc

# 또는 직접 실행  
~/.local/bin/mcp-client
```

#### macOS
```bash
# pipx 설치
brew install pipx
pipx ensurepath

# 프로젝트 설치
pipx install git+https://github.com/jih4855/MCP_cli_client.git

# 어디서든 실행
mcp-client
```

#### CentOS/RHEL/Rocky Linux
```bash
# Python 및 pipx 설치
sudo dnf install python3-pip
pip3 install --user pipx
pipx ensurepath

# 프로젝트 설치
pipx install git+https://github.com/jih4855/MCP_cli_client.git

# 어디서든 실행
mcp-client
```

### 글로벌 설치 (macOS만 권장)

**macOS에서만 안정적으로 작동합니다.**

```bash
git clone https://github.com/jih4855/MCP_cli_client.git
cd MCP_cli_client
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
mcp-client
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

3. **MCP server 설정** (`src/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "ubuntu-info-server": {
      "command": "python",
      "args": ["UPDATE_THIS_PATH/mcp_server/MCP_official.py"],
      "description": "시간 및 시스템 정보 도구"
    }
  }
}
```

**⚠️ 경로 설정 필수**: 
- `ubuntu-info-server`의 `args` 경로를 **실제 서버 경로**로 수정
- pipx 설치 후 MCP 서버 파일을 서버에 복사 또는 git clone 필요

**빠른 설정 예시**:
```bash
# 1. 프로젝트 클론 (MCP 서버 파일용)  
git clone https://github.com/jih4855/MCP_cli_client.git ~/mcp-project

# 2. 설정 파일들 복사 및 생성  
cp ~/mcp-project/src/config/config.yaml ~/config.yaml 2>/dev/null || cat > ~/config.yaml << 'EOF'
system_prompt: |
  당신은 도움이 되는 AI assistant입니다.
  
model: gemini-2.5-flash
provider: gemini  
api_base: None
max_context: 20
session_id: "default"
EOF

cat > ~/.env << 'EOF'
api_key=your_gemini_api_key_here
EOF

# MCP 설정 자동 수정
sed -i 's|UPDATE_THIS_PATH|/home/'$(whoami)'/mcp-project|g' ~/mcp-project/src/config/mcp_config.json
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
🔍 서버 설정: ['ubuntu-info-server']
🧠 LLM 초기화 완료: gemini-2.5-flash (gemini)

user: 현재 시간과 시스템 정보 알려줘
🔍 도구 호출: get_current_time
🔍 도구 호출: get_ubuntu_system_info
✅ 도구 실행 완료
assistant: 현재 시간은 2025년 1월 9일이고, Ubuntu 22.04 시스템에서 실행 중입니다. 
커널 버전은 5.15.0이며, 시스템 업타임은 2일 14시간입니다.

user: 끝
assistant: 대화 종료
```

## 📁 프로젝트 구조

```
typer_cli/
├── main.py                 # CLI 진입점
├── src/
│   ├── config/
│   │   └── mcp_config.json # MCP server 설정
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
    "ubuntu-info-server": {
      "command": "python",
      "args": ["UPDATE_THIS_PATH/mcp_server/MCP_official.py"],
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
assistant: 대화 종료
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
4. **사용자 입력 처리**: MCP를 통한 필요 도구 호출
5. **병렬 도구 실행**: 선택된 도구들을 동시에 실행
6. **결과 통합**: 모든 결과를 통합하여 자연어 응답 생성

### Ubuntu MCP Server 도구

- `get_ubuntu_system_info`: OS 정보, 커널, 업타임
- `get_ubuntu_memory_info`: 메모리 사용량 (`free -h`)
- `get_ubuntu_cpu_info`: CPU 정보 (`lscpu`)
- `get_ubuntu_disk_info`: 디스크 사용량 (`df -h`)
- `get_ubuntu_process_info`: 상위 CPU 사용 프로세스
- `get_ubuntu_network_info`: 네트워크 인터페이스 정보


### 개발 우선순위

- [ ] OpenAI MCP 도구 지원 완성
- [ ] Ollama MCP 도구 지원 구현  
- [ ] 더 많은 Ubuntu 도구 추가 (패키지 관리, 로그 분석 등)
- [ ] CLI 명령어 옵션 확장 (Typer 활용)
- [ ] Web UI 개발 (선택사항)

## 알려진 이슈

- OpenAI, Ollama에서 MCP 도구 지원 미완성
- 일부 Ubuntu 명령어에서 권한 문제 가능 
- 대용량 시스템 정보 출력 시 응답 지연 가능
- 네트워크 연결이 불안정할 때 MCP 서버 재연결 필요

## 📦 설치 방법 요약

| 방법 | 장점 | 단점 | 지원 환경 |
|------|------|------|----------|
| **pipx 설치** | 격리된 환경 + 글로벌 명령어, 의존성 충돌 없음 | pipx 사전 설치 필요 | ✅ **모든 환경 권장** |
| **글로벌 설치** | 어디서든 `mcp-client` 실행 | 시스템 Python에 설치, 권한 문제 | ⚠️ macOS만 권장 |
| **개발 모드** | 코드 수정 즉시 반영 | 가상환경 활성화 필요 | ✅ 개발용 |

## 🔗 관련 링크

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Anthropic MCP 가이드](https://github.com/modelcontextprotocol)
- [MCP server 목록](https://github.com/modelcontextprotocol/servers)

---

⭐ **Gemini LLM + Ubuntu MCP Server 완전 지원**
- MCP를 통한 다중 도구 병렬 실행
- 실시간 시스템 모니터링 및 정보 조회
- 글로벌 설치로 어디서든 실행 가능

🚧 **개발 진행 중**
- OpenAI, Ollama MCP 도구 지원 구현
- 더 많은 시스템 도구 및 MCP 서버 추가
