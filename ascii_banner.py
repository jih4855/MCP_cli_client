import re
import shutil

# 깔끔한 색상 팔레트
BLUE = "\033[94m"
CYAN = "\033[96m" 
GREY = "\033[90m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

# 세련된 그라데이션 색상
def soft_blue(intensity=1.0):
    r, g, b = int(100 * intensity), int(150 * intensity), int(255 * intensity)
    return f"\033[38;2;{r};{g};{b}m"

def soft_cyan(intensity=1.0):
    r, g, b = int(0 * intensity), int(200 * intensity), int(255 * intensity)
    return f"\033[38;2;{r};{g};{b}m"

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")

def _visible_length(text: str) -> int:
    return len(ANSI_PATTERN.sub("", text))

def _center(text: str, width: int) -> str:
    pad = max(0, (width - _visible_length(text)) // 2)
    return " " * pad + text

def _left_align(text: str, indent: int = 0) -> str:
    """왼쪽 정렬로 텍스트 출력"""
    return " " * indent + text

def _elegant_gradient(width: int) -> str:
    """부드러운 그라데이션 라인"""
    line = ""
    for i in range(width):
        intensity = 0.3 + 0.7 * (i / width)
        if i < width // 3:
            line += f"{soft_blue(intensity)}─{RESET}"
        elif i < 2 * width // 3:
            line += f"{soft_cyan(intensity)}─{RESET}"
        else:
            line += f"{CYAN}─{RESET}"
    return line

def print_clean_banner():
    """깔끔하고 세련된 배너 - 왼쪽 정렬"""
    
    # 더 깔끔한 ASCII 아트
    ascii_title = [
        " __  __  ____   ____        ____ _     ___       ____ _ _            _ ",
        "|  \\/  |/ ___| |  _ \\      / ___| |   |_ _|     / ___| (_) ___ _ __ | |_",
        "| |\\/| | |     | |_) |    | |   | |    | |     | |   | | |/ _ \\ '_ \\| __|",
        "| |  | | |___  |  _ <     | |___| |___ | |     | |___| | |  __/ | | | |_ ",
        "|_|  |_|\\____| |_| \\_\\     \\____|_____|___|     \\____|_|_|\\___|_| |_|\\__|",
        "                                                                      "        
    ]
    
    # 상단 여백
    print()
    
    # ASCII 아트 출력 (부드러운 블루 톤) - 왼쪽 정렬
    for line in ascii_title:
        if line.strip():
            colored_line = f"{soft_blue(0.8)}{line}{RESET}"
            print(_left_align(colored_line))
        else:
            print()
    
    print()
    
    # 세련된 타이틀 - 왼쪽 정렬
    title = f"{BOLD}{WHITE}OPEN LLM CLI{RESET}"
    print(_left_align(title))
    
    # 우아한 구분선 - 왼쪽 정렬
    gradient_line = _elegant_gradient(50)
    print(_left_align(gradient_line))
    
    print()
    
    # 깔끔한 기능 설명 - 왼쪽 정렬
    features = [
        f"{DIM}AI-Powered Command Line Interface{RESET}",
        f"{CYAN}• {RESET}Open Source LLM Integration",
        f"{CYAN}• {RESET}MCP Server Support", 
        f"{CYAN}• {RESET}Fast & Reliable Execution"
    ]
    
    for feature in features:
        print(_left_align(feature))
    
    print()

def print_minimal_banner():
    """미니멀한 한 줄 배너 - 왼쪽 정렬"""
    
    # 심플한 한 줄 - 왼쪽 정렬
    banner = f"{soft_cyan(0.9)}◦{RESET} {BOLD}OPEN LLM CLI{RESET} {soft_blue(0.9)}◦{RESET} {DIM}AI-Powered Development Tool{RESET}"
    
    print()
    print(_left_align(banner))
    
    # 미니멀 구분선 - 왼쪽 정렬
    line = f"{soft_cyan(0.5)}{'─' * 30}{RESET}"
    print(_left_align(line))
    print()

if __name__ == "__main__":
    print_clean_banner()
    print("\n" + "─" * 60 + "\n")
    print_minimal_banner()