import subprocess
import re
import requests
import urllib3
import os
import sys
from datetime import datetime

# 添加父目录到路径，以便导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROCESS_NAME = "LeagueClientUx.exe"

def get_lcu_credentials():
    """
    通过Windows命令行获取LCU API的端口和认证Token。
    这是与客户端交互的关键。
    
    返回:
        tuple: (port, token) - 成功返回端口和认证令牌，失败返回(None, None)
    """
    try:
        # 使用PowerShell来获取更详细的进程信息
        powershell_command = f'powershell "Get-WmiObject Win32_Process -Filter \\"name = \'{PROCESS_NAME}\'\\"|Select-Object CommandLine | Format-List"'
        print(f"执行命令: {powershell_command}")
        
        output = subprocess.check_output(powershell_command, shell=True, text=True, stderr=subprocess.DEVNULL)
        print(f"命令输出长度: {len(output)} 字符")
        
        # 输出前500个字符以便检查
        preview = output[:500] + "..." if len(output) > 500 else output
        print(f"输出预览: \n{preview}")

        # 使用正则表达式从命令行参数中提取端口和Token
        port_match = re.search(r'--app-port=(\d+)', output)
        token_match = re.search(r'--remoting-auth-token=([\w-]+)', output)

        if port_match:
            port = port_match.group(1)
            print(f"找到端口: {port}")
        else:
            print("未找到端口")
            port = None
            
        if token_match:
            token = token_match.group(1)
            print(f"找到令牌: {token}")
        else:
            print("未找到令牌")
            token = None

        if port and token:
            # 返回端口和认证密码
            return port, token
        else:
            print("警告: 无法从进程参数中提取端口和令牌")
            return None, None
    except subprocess.SubprocessError as e:
        print(f"subprocess错误: {e}")
        return None, None
    except Exception as e:
        # 如果客户端未运行或命令执行失败，则返回None
        print(f"获取LCU凭证时发生错误: {e}")
        return None, None


def test_lcu_connection(port, token):
    """测试LCU连接是否有效"""
    if not port or not token:
        print("端口或令牌为空，无法测试连接")
        return False
        
    try:
        # 创建不验证SSL证书的Session
        session = requests.Session()
        session.verify = False
        
        # 尝试一个基本的LCU端点，通常总是可用的
        test_url = f"https://127.0.0.1:{port}/lol-summoner/v1/current-summoner"
        auth = requests.auth.HTTPBasicAuth('riot', token)
        
        print(f"尝试连接: {test_url}")
        response = session.get(test_url, auth=auth, timeout=3)
        
        # 打印完整的响应信息
        print(f"响应状态码: {response.status_code}")
        try:
            if response.content:
                content_preview = response.content[:100] + b"..." if len(response.content) > 100 else response.content
                print(f"响应内容预览: {content_preview}")
        except Exception as e:
            print(f"读取响应内容时出错: {e}")
        
        # 检查状态码，即使是401也表示服务器正在响应
        if response.status_code != 0:
            print("LCU连接测试成功")
            return True
        else:
            print("LCU连接测试失败: 无响应")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"LCU连接测试失败: 连接错误 - {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"LCU连接测试失败: 连接超时 - {e}")
        return False
    except Exception as e:
        print(f"LCU连接测试失败: {e}")
        return False


def test_alternate_endpoints(port, token):
    """测试其他几个常用的端点，帮助找出哪些是可访问的"""
    if not port or not token:
        print("端口或令牌为空，无法测试端点")
        return
    
    # 创建不验证SSL证书的Session
    session = requests.Session()
    session.verify = False
    auth = requests.auth.HTTPBasicAuth('riot', token)
    
    # 一些常用的端点
    endpoints = [
        "/lol-summoner/v1/current-summoner",
        "/lol-end-of-game/v1/eog-stats-block",
        "/lol-match-history/v1/games/recent",
        "/lol-end-of-game/v1/gameclient-eog-stats-block",
        "/lol-match-history/v1/match-history",
        "/lol-champions/v1/owned-champions-minimal",
        "/lol-game-queues/v1/queues",
        "/lol-inventory/v2/inventory",
        "/lol-ranked/v1/ranked-stats"
    ]
    
    print("\n测试多个端点:")
    for endpoint in endpoints:
        try:
            test_url = f"https://127.0.0.1:{port}{endpoint}"
            print(f"\n尝试访问: {test_url}")
            response = session.get(test_url, auth=auth, timeout=3)
            
            content_length = len(response.content) if response.content else 0
            print(f"状态码: {response.status_code}, 内容长度: {content_length} 字节")
            
            if response.status_code == 200 and content_length > 0:
                print(f"成功 ✓ - 端点可用: {endpoint}")
            else:
                print(f"失败 ✗ - 状态码: {response.status_code}")
        except Exception as e:
            print(f"错误 ✗ - {str(e)}")


def list_running_processes(save_to_file=True):
    """
    列出当前系统中正在运行的进程
    
    参数:
        save_to_file: 是否将进程列表保存到文件中
    """
    try:
        print("\n正在获取系统中运行的进程列表...")
        command = "wmic process get name,processid"
        output = subprocess.check_output(command, shell=True, text=True)
        
        # 处理输出，按行分割并移除空行
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        if lines:
            # 创建要显示和保存的内容
            process_list_content = []
            
            # 添加表头
            header_line = f"{'进程名称':<40} {'进程ID':<10}"
            divider_line = "-" * 50
            process_list_content.append(header_line)
            process_list_content.append(divider_line)
            
            # 打印表头
            print(f"\n{header_line}")
            print(divider_line)
            
            # 处理并显示每一行
            for line in lines[1:]:  # 跳过表头行
                # 分割进程名和ID，确保有足够的部分
                parts = line.split()
                if parts:
                    # 最后一个部分是PID，其余的是进程名称
                    pid = parts[-1]
                    name = ' '.join(parts[:-1])
                    formatted_line = f"{name:<40} {pid:<10}"
                    print(formatted_line)
                    process_list_content.append(formatted_line)
            
            total_processes = len(lines) - 1
            summary_line = f"\n总共找到 {total_processes} 个进程"
            print(summary_line)
            process_list_content.append(summary_line)
            
            # 保存到文件
            if save_to_file:
                # 创建目录(如果不存在)
                logs_dir = "process_logs"
                if not os.path.exists(logs_dir):
                    os.makedirs(logs_dir)
                
                # 使用时间戳创建文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(logs_dir, f"processes_{timestamp}.txt")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(process_list_content))
                
                print(f"\n进程列表已保存到: {file_path}")
        else:
            print("未找到任何进程信息")
            
    except subprocess.SubprocessError as e:
        print(f"获取进程列表时出错 (SubprocessError): {e}")
    except Exception as e:
        print(f"获取进程列表时出错: {e}")


if __name__ == "__main__":
    # 首先列出系统中的进程，帮助用户查看是否有客户端进程
    list_running_processes()
    
    print("\n开始获取LCU凭证...")
    port, token = get_lcu_credentials()
    
    if port and token:
        print(f"\n成功获取凭证 - 端口: {port}, 令牌: {token}")
        
        # 测试连接
        print("\n测试LCU连接...")
        if test_lcu_connection(port, token):
            print("\n连接测试成功，现在测试各个端点...")
            test_alternate_endpoints(port, token)
        else:
            print("\n连接测试失败，请确保英雄联盟客户端正在运行")
    else:
        print("\n获取凭证失败，请确保英雄联盟客户端正在运行")
        print("\n【重要提示】由于系统安全限制，获取LCU进程参数需要管理员权限。")
        print("请以管理员身份重新运行此脚本：")
        print("1. 右键点击命令提示符(cmd)或PowerShell，选择\"以管理员身份运行\"")
        print("2. 导航到脚本所在目录")
        print("3. 执行命令: python test_lcu_credentials.py")
