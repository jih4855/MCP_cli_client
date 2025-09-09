import asyncio
import subprocess
import os
import platform
import json
from datetime import datetime
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

server = Server("ubuntu-info-server")

# 안전한 Ubuntu 명령어 화이트리스트
SAFE_UBUNTU_COMMANDS = {
    "system_info": ["uname", "-a"],
    "os_info": ["lsb_release", "-a"],
    "hardware_info": ["lscpu"],
    "memory_info": ["free", "-h"],
    "disk_info": ["df", "-h"],
    "cpu_info": ["cat", "/proc/cpuinfo"],
    "uptime": ["uptime"],
    "network_interfaces": ["ip", "addr", "show"],
    "processes": ["ps", "aux", "--sort=-%cpu", "--no-headers"],
    "kernel_version": ["uname", "-r"],
    "current_user": ["whoami"],
    "hostname": ["hostname"],
    "timezone": ["timedatectl", "show", "--property=Timezone", "--value"],
    "load_average": ["cat", "/proc/loadavg"],
    "disk_usage": ["du", "-sh", "/", "/home", "/var", "/tmp"],
    "package_count": ["dpkg", "--get-selections", "|", "wc", "-l"],
}

def run_safe_command(command_key: str) -> str:
    """안전한 Ubuntu 명령어만 실행"""
    if command_key not in SAFE_UBUNTU_COMMANDS:
        return f"❌ 허용되지 않은 명령어: {command_key}"
    
    try:
        cmd = SAFE_UBUNTU_COMMANDS[command_key]
        
        # 파이프가 포함된 명령어는 shell=True로 실행
        if "|" in " ".join(cmd):
            result = subprocess.run(
                " ".join(cmd),
                shell=True,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                timeout=15  # Ubuntu는 15초 타임아웃
            )
        else:
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                timeout=15
            )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"❌ 명령어 실행 실패: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "❌ 명령어 실행 시간 초과"
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """사용 가능한 도구 목록 반환"""
    return [
        types.Tool(
            name="get_current_time",
            description="현재 시간을 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_ubuntu_system_info",
            description="Ubuntu 시스템 전체 정보를 조회합니다 (OS 버전, 커널, 하드웨어 등)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_ubuntu_memory_info",
            description="Ubuntu 메모리 사용량 정보를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_ubuntu_disk_info",
            description="Ubuntu 디스크 사용량 정보를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_ubuntu_cpu_info",
            description="Ubuntu CPU 정보를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_ubuntu_process_info",
            description="Ubuntu 실행 중인 프로세스 정보를 조회합니다 (CPU 사용률 순)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_ubuntu_network_info",
            description="Ubuntu 네트워크 인터페이스 정보를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_available_commands",
            description="사용 가능한 Ubuntu 정보 조회 명령어 목록을 보여줍니다",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """도구 실행 핸들러"""
    
    if name == "get_current_time":
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return [types.TextContent(type="text", text=current_time)]
    
    elif name == "get_ubuntu_system_info":
        try:
            info = {}
            
            # Ubuntu OS 정보
            os_info = run_safe_command("os_info")
            info["OS_Info"] = os_info.replace('\n', ' | ') if not os_info.startswith("❌") else "Unknown"
            
            # 시스템 정보
            system_info = run_safe_command("system_info")
            info["System_Info"] = system_info if not system_info.startswith("❌") else "Unknown"
            
            # 커널 버전
            kernel = run_safe_command("kernel_version")
            info["Kernel_Version"] = kernel if not kernel.startswith("❌") else "Unknown"
            
            # 현재 사용자
            user = run_safe_command("current_user")
            info["Current_User"] = user if not user.startswith("❌") else "Unknown"
            
            # 호스트명
            hostname = run_safe_command("hostname")
            info["Hostname"] = hostname if not hostname.startswith("❌") else "Unknown"
            
            # 업타임
            uptime = run_safe_command("uptime")
            info["Uptime"] = uptime if not uptime.startswith("❌") else "Unknown"
            
            # 타임존
            timezone = run_safe_command("timezone")
            info["Timezone"] = timezone if not timezone.startswith("❌") else "Unknown"
            
            # 로드 평균
            load_avg = run_safe_command("load_average")
            info["Load_Average"] = load_avg if not load_avg.startswith("❌") else "Unknown"
            
            result = json.dumps(info, indent=2, ensure_ascii=False)
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ 시스템 정보 수집 실패: {str(e)}"
            return [types.TextContent(type="text", text=error_msg)]
    
    elif name == "get_ubuntu_memory_info":
        memory_info = run_safe_command("memory_info")
        result = f"🧠 메모리 정보:\n{memory_info}"
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_ubuntu_disk_info":
        disk_info = run_safe_command("disk_info")
        result = f"💾 디스크 정보:\n{disk_info}"
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_ubuntu_cpu_info":
        cpu_info = run_safe_command("hardware_info")  # lscpu 사용
        result = f"🖥️ CPU 정보:\n{cpu_info[:1000]}..."  # 너무 길어질 수 있으니 제한
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_ubuntu_process_info":
        process_info = run_safe_command("processes")
        # 상위 10개 프로세스만 표시
        lines = process_info.split('\n')[:10]
        result = f"🔄 상위 CPU 사용 프로세스:\n" + '\n'.join(lines)
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_ubuntu_network_info":
        network_info = run_safe_command("network_interfaces")
        # 요약된 네트워크 정보
        lines = network_info.split('\n')
        summary = []
        current_interface = None
        
        for line in lines:
            line = line.strip()
            if line and ': ' in line and 'state' in line.lower():
                parts = line.split(':')[0]
                current_interface = parts.split()[-1] if parts else None
                summary.append(f"📡 {current_interface}")
            elif 'inet ' in line and current_interface:
                ip_part = line.split('inet ')[1].split()[0] if 'inet ' in line else ""
                summary.append(f"   IP: {ip_part}")
        
        result = '\n'.join(summary[:15])  # 최대 15줄만
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_available_commands":
        commands = list(SAFE_UBUNTU_COMMANDS.keys())
        result = f"📋 사용 가능한 Ubuntu 명령어:\n" + '\n'.join([f"• {cmd}" for cmd in commands])
        return [types.TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # stdio를 통해 MCP 서버 실행
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ubuntu-info-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())