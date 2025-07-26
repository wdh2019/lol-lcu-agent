import subprocess
import re
import requests
import os
from .system_utils import list_running_processes

def get_lcu_credentials(lcu_port="", lcu_token="", log_manager=None):
    """
    通过Windows命令行获取LCU API的端口和认证Token。
    这是与客户端交互的关键。
    
    参数:
        lcu_port: 预设的LCU端口，如果动态获取失败将使用此值
        lcu_token: 预设的LCU令牌，如果动态获取失败将使用此值
        log_manager: 日志管理器，如果提供则记录日志
        
    返回:
        tuple: (port, token) - 成功返回端口和认证令牌，失败返回(None, None)
    """
    try:
        # 首先尝试通过命令行动态获取
        log_msg = "尝试通过命令行动态获取LCU凭证..."
        print(log_msg)
        if log_manager:
            log_manager.info(log_msg)
            
        # 尝试使用PowerShell获取更可靠的结果
        powershell_command = f'powershell "Get-WmiObject Win32_Process -Filter \\"name = \'LeagueClientUx.exe\'\\"|Select-Object CommandLine | Format-List"'
        log_msg = f"执行命令: {powershell_command}"
        print(log_msg)
        if log_manager:
            log_manager.debug(log_msg)
        
        output = subprocess.check_output(powershell_command, shell=True, text=True, stderr=subprocess.DEVNULL)
        log_msg = f"命令输出长度: {len(output)} 字符"
        print(log_msg)
        if log_manager:
            log_manager.debug(log_msg)
        
        # 输出前500个字符以便检查
        preview = output[:500] + "..." if len(output) > 500 else output
        log_msg = f"输出预览: \n{preview}"
        print(log_msg)
        if log_manager:
            log_manager.debug(log_msg)

        # 使用正则表达式从命令行参数中提取端口和Token
        port_match = re.search(r'--app-port=(\d+)', output)
        token_match = re.search(r'--remoting-auth-token=([\w-]+)', output)

        if port_match:
            port = port_match.group(1)
            log_msg = f"找到端口: {port}"
            print(log_msg)
            if log_manager:
                log_manager.info(log_msg)
        else:
            log_msg = "未找到端口"
            print(log_msg)
            if log_manager:
                log_manager.warning(log_msg)
            port = None
            
        if token_match:
            token = token_match.group(1)
            log_msg = f"找到令牌: {token[:5]}..." # 只显示令牌前几位，避免安全风险
            print(log_msg)
            if log_manager:
                log_manager.info(log_msg)
        else:
            log_msg = "未找到令牌"
            print(log_msg)
            if log_manager:
                log_manager.warning(log_msg)
            token = None

        if port and token:
            # 返回端口和认证密码
            return port, token
        else:
            # 如果动态获取失败，使用预定义的凭证
            if lcu_port and lcu_token:
                log_msg = f"动态获取失败，尝试使用预定义的LCU凭证(端口:{lcu_port})"
                print(log_msg)
                if log_manager:
                    log_manager.warning(log_msg)
                return lcu_port, lcu_token
            else:
                log_msg = "警告: 无法从进程参数中提取端口和令牌，且无预定义凭证"
                print(log_msg)
                if log_manager:
                    log_manager.error(log_msg)
                return None, None
    except subprocess.SubprocessError as e:
        error_msg = f"subprocess错误: {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
        
        tip_msg = "\n【重要提示】由于系统安全限制，获取LCU进程参数需要管理员权限。\n" + \
                  "请以管理员身份重新运行此脚本：\n" + \
                  "1. 右键点击命令提示符(cmd)或PowerShell，选择\"以管理员身份运行\"\n" + \
                  "2. 导航到脚本所在目录\n" + \
                  "3. 执行命令: python main.py"
        print(tip_msg)
        if log_manager:
            log_manager.warning(tip_msg)
        
        # 列出当前系统中的进程，帮助用户查看是否有客户端进程
        list_running_processes(log_manager)
        return None, None
    except Exception as e:
        # 如果客户端未运行或命令执行失败，则返回None
        error_msg = f"获取LCU凭证时发生错误: {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
        
        tip_msg = "\n【重要提示】无法获取LCU凭证，可能的原因:\n" + \
                  "1. 英雄联盟客户端未启动\n" + \
                  "2. 需要管理员权限才能获取进程参数\n" + \
                  "请确保客户端正在运行，然后以管理员身份运行此脚本"
        print(tip_msg)
        if log_manager:
            log_manager.warning(tip_msg)
        
        # 列出当前系统中的进程，帮助用户查看是否有客户端进程
        list_running_processes(log_manager)
        return None, None


def test_lcu_connection(port, token, session, log_manager=None):
    """
    测试LCU连接是否有效
    
    参数:
        port: LCU端口
        token: LCU认证令牌
        session: requests会话
        log_manager: 日志管理器，如果提供则记录日志
        
    返回:
        bool: 连接成功返回True，失败返回False
    """
    if not port or not token:
        if log_manager:
            log_manager.warning("LCU连接测试失败: 端口或令牌为空")
        print("LCU连接测试失败: 端口或令牌为空")
        return False
        
    try:
        # 尝试一个基本的LCU端点，通常总是可用的
        test_url = f"https://127.0.0.1:{port}/lol-summoner/v1/current-summoner"
        auth = requests.auth.HTTPBasicAuth('riot', token)
        response = session.get(test_url, auth=auth, timeout=3)
        
        # 检查状态码，即使是401也表示服务器正在响应
        if response.status_code != 0:
            success_msg = f"LCU连接测试成功，状态码: {response.status_code}"
            print(success_msg)
            if log_manager:
                log_manager.info(success_msg)
            return True
        else:
            error_msg = "LCU连接测试失败: 无响应"
            print(error_msg)
            if log_manager:
                log_manager.error(error_msg)
            return False
    except requests.exceptions.ConnectionError as e:
        error_msg = f"LCU连接测试失败: 连接错误 - {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
        return False
    except requests.exceptions.Timeout:
        error_msg = "LCU连接测试失败: 连接超时"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
        return False
    except Exception as e:
        error_msg = f"LCU连接测试失败: {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
        return False
