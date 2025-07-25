import subprocess
import re
import requests
import os
from system_utils import list_running_processes

def get_lcu_credentials(lcu_port="", lcu_token=""):
    """
    通过Windows命令行获取LCU API的端口和认证Token。
    这是与客户端交互的关键。
    
    参数:
        lcu_port: 预设的LCU端口，如果动态获取失败将使用此值
        lcu_token: 预设的LCU令牌，如果动态获取失败将使用此值
        
    返回:
        tuple: (port, token) - 成功返回端口和认证令牌，失败返回(None, None)
    """
    try:
        # 首先尝试通过命令行动态获取
        print("尝试通过命令行动态获取LCU凭证...")
        # 尝试使用PowerShell获取更可靠的结果
        powershell_command = f'powershell "Get-WmiObject Win32_Process -Filter \\"name = \'LeagueClientUx.exe\'\\"|Select-Object CommandLine | Format-List"'
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
            # 如果动态获取失败，使用预定义的凭证
            if lcu_port and lcu_token:
                print(f"动态获取失败，尝试使用预定义的LCU凭证(端口:{lcu_port})")
                return lcu_port, lcu_token
            else:
                print("警告: 无法从进程参数中提取端口和令牌，且无预定义凭证")
                return None, None
    except subprocess.SubprocessError as e:
        print(f"subprocess错误: {e}")
        print("\n【重要提示】由于系统安全限制，获取LCU进程参数需要管理员权限。")
        print("请以管理员身份重新运行此脚本：")
        print("1. 右键点击命令提示符(cmd)或PowerShell，选择\"以管理员身份运行\"")
        print("2. 导航到脚本所在目录")
        print("3. 执行命令: python main.py")
        # 列出当前系统中的进程，帮助用户查看是否有客户端进程
        list_running_processes()
        return None, None
    except Exception as e:
        # 如果客户端未运行或命令执行失败，则返回None
        print(f"获取LCU凭证时发生错误: {e}")
        print("\n【重要提示】无法获取LCU凭证，可能的原因:")
        print("1. 英雄联盟客户端未启动")
        print("2. 需要管理员权限才能获取进程参数")
        print("请确保客户端正在运行，然后以管理员身份运行此脚本")
        # 列出当前系统中的进程，帮助用户查看是否有客户端进程
        list_running_processes()
        return None, None


def test_lcu_connection(port, token, session):
    """
    测试LCU连接是否有效
    
    参数:
        port: LCU端口
        token: LCU认证令牌
        session: requests会话
        
    返回:
        bool: 连接成功返回True，失败返回False
    """
    if not port or not token:
        return False
        
    try:
        # 尝试一个基本的LCU端点，通常总是可用的
        test_url = f"https://127.0.0.1:{port}/lol-summoner/v1/current-summoner"
        auth = requests.auth.HTTPBasicAuth('riot', token)
        response = session.get(test_url, auth=auth, timeout=3)
        
        # 检查状态码，即使是401也表示服务器正在响应
        if response.status_code != 0:
            print(f"LCU连接测试成功，状态码: {response.status_code}")
            return True
        else:
            print("LCU连接测试失败: 无响应")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"LCU连接测试失败: 连接错误 - {e}")
        return False
    except requests.exceptions.Timeout:
        print("LCU连接测试失败: 连接超时")
        return False
    except Exception as e:
        print(f"LCU连接测试失败: {e}")
        return False
