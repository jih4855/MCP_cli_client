import json
import subprocess

import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import importlib.resources
import sys
import shutil
from mcp.client.stdio import stdio_client
import ast
import importlib.resources
import sys
import shutil


class MCPmanager:
    def __init__(self, config_path="mcp_config.json"):
        self.client_session = None
        self.config_path = config_path
        self.server_sessions = {}
        self.server_configs = {}
        self.connections = {}
        self.sessions = {}
        self.active_connections = {}
        self.failed_servers = {}

    def load_config(self):
        try:
            with importlib.resources.open_text("src.config", "mcp_config.json") as f:
                config = json.load(f)
                self.server_configs = config.get("mcpServers", {})
                print(f"✅ MCP 설정 로드 완료: {list(self.server_configs.keys())}")
        except FileNotFoundError:
            print("mcp_config.json 파일을 찾을 수 없습니다.")
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")

    async def _start_server_process(self, name: str, cmd: str, args: list):
        """단일 MCP 서버 프로세스 시작(세션 반환)"""
        server_params = StdioServerParameters(command=cmd, args=args)
        connection = stdio_client(server_params)
        read, write = await connection.__aenter__()
        session_obj = ClientSession(read, write)
        session = await session_obj.__aenter__()
        await session.initialize()
        self.connections[name] = connection
        return session

    async def start_server(self, server_name: str):
        if server_name not in self.server_configs:
            print(f"❌ {server_name} 서버 설정이 없습니다.")
            return False
        cfg = self.server_configs[server_name]
        cmd = cfg.get("command")
        args = cfg.get("args", [])

        if not cmd or shutil.which(cmd) is None:
            if cmd in (None, "", "python", "python3"):
                cmd = sys.executable
            else:
                print(f"[MCP][WARN] '{server_name}' command 찾기 실패: {cmd}")
                self.failed_servers[server_name] = "command-not-found"
                return False
        try:
            session = await self._start_server_process(server_name, cmd, args)
            self.sessions[server_name] = session
            print(f"✅ {server_name} MCP 서버 시작 완료 ({cmd})")
            return True
        except Exception as e:
            print(f"❌ {server_name} 서버 시작 실패: {e}")
            self.failed_servers[server_name] = str(e)
            return False

    async def start_all_servers(self):
        self.sessions = {}
        self.failed_servers = {}
        for name, cfg in self.server_configs.items():
            cmd = cfg.get("command")
            args = cfg.get("args", [])
            if not cmd or shutil.which(cmd) is None:
                if cmd in (None, "", "python", "python3"):
                    cmd = sys.executable
                else:
                    print(f"[MCP][WARN] '{name}' command 없음: {cmd} -> 건너뜀")
                    self.failed_servers[name] = "command-not-found"
                    continue
            try:
                session = await self._start_server_process(name, cmd, args)
                self.sessions[name] = session
                print(f"[MCP] 서버 시작 성공: {name}")
            except Exception as e:
                self.failed_servers[name] = str(e)
                print(f"[MCP][ERROR] 서버 시작 실패: {name} -> {e}")

    async def execute_tool(self, server_name, tool_name, params):
        session = self.sessions.get(server_name)
        if not session:
            raise RuntimeError(f"[MCP] 세션 없음: {server_name}")
        return await session.call_tool(tool_name, params)

    async def multi_execute_tool(self, tool_name, params):
        tasks = [self.execute_tool(s, tool_name, params) for s in self.sessions]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all_servers(self):
        for name, conn in list(self.connections.items()):
            try:
                await self.sessions[name].__aexit__(None, None, None)
                await conn.__aexit__(None, None, None)
                print(f"[MCP] 서버 종료: {name}")
            except Exception as e:
                print(f"[MCP][WARN] 종료 실패 {name}: {e}")
        self.sessions.clear()
        self.connections.clear()
        self.failed_servers = {}

        for name, cfg in self.server_configs.items():
            cmd = cfg.get("command")
            args = cfg.get("args", [])

            if not cmd or shutil.which(cmd) is None:
                if cmd in (None, "", "python", "python3"):
                    cmd = sys.executable
                else:
                    print(f"[MCP][WARN] '{name}' command 없음: {cmd} -> 건너뜀")
                    self.failed_servers[name] = "command-not-found"
                    continue
            try:
                session = await self._start_server_process(name, cmd, args)
                self.sessions[name] = session
                print(f"[MCP] 서버 시작 성공: {name}")
            except Exception as e:
                self.failed_servers[name] = str(e)
                print(f"[MCP][ERROR] 서버 시작 실패: {name} -> {e}")

    async def get_available_tools(self, server_name):
        session = self.sessions.get(server_name)
        if not session:
            raise RuntimeError(f"[MCP] 세션 없음: {server_name} (실패: {self.failed_servers.get(server_name)})")
        return await session.list_tools()
    
    async def multi_execute_tool(self, tool_name, params):
        tasks = []
        for server_name in self.sessions:
            tasks.append(self.execute_tool(server_name, tool_name, params))
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all_servers(self):
        for name, conn in list(self.connections.items()):
            try:
                # 연결 닫기
                await self.sessions[name].__aexit__(None, None, None)
                await conn.__aexit__(None, None, None)
                print(f"[MCP] 서버 종료: {name}")
            except Exception as e:
                print(f"[MCP][WARN] 종료 실패 {name}: {e}")
        self.sessions.clear()
        self.connections.clear()