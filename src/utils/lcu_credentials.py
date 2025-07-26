import subprocess
import re
import requests
import os
import ctypes
from .system_utils import list_running_processes
from .log_manager import get_logger

def is_admin():
    """检查当前进程是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

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
    # 使用单例日志管理器
    log_manager = get_logger()
    
    # 检查管理员权限
    if not is_admin():
        error_msg = "警告: 当前进程没有管理员权限，可能无法获取LCU进程信息"
        print(error_msg)
        if log_manager:
            log_manager.warning(error_msg)
    else:
        success_msg = "确认: 当前进程具有管理员权限"
        print(success_msg)
        if log_manager:
            log_manager.info(success_msg)
            
    try:
        # 首先尝试通过命令行动态获取
        log_msg = "尝试通过命令行动态获取LCU凭证..."
        print(log_msg)
        if log_manager:
            log_manager.info(log_msg)
            
        # 使用wmic命令获取进程信息，通常能更好地继承管理员权限
        wmic_command = 'wmic process where name="LeagueClientUx.exe" get commandline /format:list'
        
        log_msg = f"执行命令: {wmic_command}"
        print(log_msg)
        if log_manager:
            log_manager.debug(log_msg)
        
        # 创建subprocess时使用管理员权限
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        output = subprocess.check_output(
            wmic_command, 
            shell=True, 
            text=True, 
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo
        )
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
        log_msg = f"port_match: {port_match}, token_match: {token_match}"
        print(log_msg)
        log_manager.info(log_msg)

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
        error_msg = f"WMIC命令执行错误: {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
        
        tip_msg = "\n【重要提示】WMIC命令执行失败，可能的原因:\n" + \
                  "1. 程序没有以管理员权限运行\n" + \
                  "2. WMI服务未启动或异常\n" + \
                  "3. 系统权限限制\n" + \
                  "建议解决方案:\n" + \
                  "- 右键以管理员身份运行程序\n" + \
                  "- 确保Windows Management Instrumentation服务正在运行"
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
                  "2. 程序需要管理员权限才能获取进程参数\n" + \
                  "3. WMI服务异常\n" + \
                  "建议解决方案:\n" + \
                  "- 确保客户端正在运行\n" + \
                  "- 右键以管理员身份运行程序\n" + \
                  "- 检查Windows服务是否正常"
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
