import json
import subprocess
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ast

class MCPmanager:
    def __init__(self, config_path="mcp_config.json"):
        self.client_session = None
        self.config_path = config_path
        self.server_sessions = {}
        self.server_configs = {}
        self.connections = {}  
        self.sessions = {}
        self.active_connections = {}  # 연결 유지용     

    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.server_configs = config.get("mcpServers", {})
                print(f"✅ MCP 설정 로드 완료: {list(self.server_configs.keys())}")
        except FileNotFoundError:
            print("mcp_config.json 파일을 찾을 수 없습니다. 파일을 생성하고 설정을 추가하세요.")
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")

    async def start_server(self, server_name):
      if server_name not in self.server_configs:
          print(f"❌ {server_name} 서버 설정을 찾을 수 없습니다.")
          return False

      config = self.server_configs[server_name]
      server_params = StdioServerParameters(
          command=config["command"],
          args=config["args"]
      )

      try:
          # 연결을 계속 유지하도록 수정
          connection = stdio_client(server_params)
          read, write = await connection.__aenter__()

          session_obj = ClientSession(read, write)
          session = await session_obj.__aenter__()
          await session.initialize()

          # 연결 정보 저장 (닫지 않도록)
          self.connections[server_name] = connection
          self.sessions[server_name] = session

          print(f"✅ {server_name} MCP 서버 시작 완료")
          return True

      except Exception as e:
          print(f"❌ {server_name} 서버 시작 실패: {e}")
          return False

    async def start_all_servers(self):
      tasks = [self.start_server(name) for name in self.server_configs]
      await asyncio.gather(*tasks)

    async def get_available_tools(self, server_name):
        session = self.sessions[server_name]
        tools = await session.list_tools()  # MCP 서버의 도구들 확인
        return tools

    async def execute_tool(self, server_name, tool_name, params):
        session = self.sessions[server_name]
        result = await session.call_tool(tool_name, params)
        return result
    
    async def multi_execute_tool(self, tool_name, params):
        tasks = []
        for server_name in self.sessions:
            tasks.append(self.execute_tool(server_name, tool_name, params))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results