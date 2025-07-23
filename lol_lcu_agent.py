import requests
import json
import time
import os
import subprocess
import re
import datetime

# --- 配置区 ---
# Live Client Data API (游戏内实时数据)
LIVE_DATA_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"
# LCU API (客户端API) 的赛后数据端点 - 提供多个可能的端点
LCU_EOG_ENDPOINTS = [
    "/lol-end-of-game/v1/eog-stats-block",
    "/lol-match-history/v1/games/recent",
    "/lol-end-of-game/v1/gameclient-eog-stats-block"
]

# 本地日志文件夹
LOG_DIR_BASE_LIVE = "game_logs_live"
LOG_DIR_BASE_POSTGAME = "game_logs_postgame"
# 当前游戏的日志文件夹（会在游戏开始时设置）
CURRENT_GAME_LOG_DIR_LIVE = ""
CURRENT_GAME_LOG_DIR_POSTGAME = ""
# 轮询间隔（秒）
POLL_INTERVAL = 5  # 减小轮询间隔，提高响应速度
# 赛后数据最大等待时间（秒）
MAX_EOG_WAIT_TIME = 120  # 等待2分钟

# --- 全局变量 ---
# 创建一个不验证SSL证书的Session，方便复用
session = requests.Session()
session.verify = False


def get_lcu_credentials():
    """
    通过Windows命令行获取LCU API的端口和认证Token。
    这是与客户端交互的关键。
    """
    try:
        # 运行wmic命令获取英雄联盟客户端的启动命令行参数
        command = "wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline"
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)

        # 使用正则表达式从命令行参数中提取端口和Token
        port_match = re.search(r'--app-port=(\d+)', output)
        token_match = re.search(r'--remoting-auth-token=([\w-]+)', output)

        if port_match and token_match:
            port = port_match.group(1)
            token = token_match.group(1)
            # 返回端口和认证密码
            return port, token
        else:
            print("警告: 无法从进程参数中提取端口和令牌，使用默认值。")
            return "2999", "riot"  # 尝试使用Live Client Data API端口
    except subprocess.SubprocessError as e:
        print(f"subprocess错误: {e}")
        return None, None
    except Exception as e:
        # 如果客户端未运行或命令执行失败，则返回None
        print(f"获取LCU凭证时发生错误: {e}")
        return None, None


def setup_directories():
    """检查并创建用于存放日志的文件夹"""
    for dir_name in [LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME]:
        if not os.path.exists(dir_name):
            print(f"基础日志文件夹 '{dir_name}' 不存在，正在创建...")
            os.makedirs(dir_name)
            
def create_game_directories():
    """为当前游戏创建一个新的文件夹，用时间戳命名"""
    global CURRENT_GAME_LOG_DIR_LIVE, CURRENT_GAME_LOG_DIR_POSTGAME
    
    # 生成当前时间戳作为文件夹名
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    
    # 为当前游戏创建新的文件夹
    CURRENT_GAME_LOG_DIR_LIVE = os.path.join(LOG_DIR_BASE_LIVE, timestamp)
    CURRENT_GAME_LOG_DIR_POSTGAME = os.path.join(LOG_DIR_BASE_POSTGAME, timestamp)
    
    # 创建文件夹
    os.makedirs(CURRENT_GAME_LOG_DIR_LIVE, exist_ok=True)
    os.makedirs(CURRENT_GAME_LOG_DIR_POSTGAME, exist_ok=True)
    
    print(f"已为当前游戏创建新的数据文件夹: {timestamp}")


def test_lcu_connection(port, token):
    """测试LCU连接是否有效"""
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


def save_data_to_json(data, data_type):
    """将获取到的数据保存为格式化的JSON文件"""
    # 使用当前游戏的日志文件夹
    log_dir = CURRENT_GAME_LOG_DIR_LIVE if data_type == 'live' else CURRENT_GAME_LOG_DIR_POSTGAME
    try:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(log_dir, f"data_{timestamp}.json")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"[{time.strftime('%H:%M:%S')}] 成功获取 [{data_type}] 数据并保存到: {filename}")

    except Exception as e:
        print(f"保存文件时出错: {e}")


def main():
    """程序主逻辑，包含状态机"""
    setup_directories()

    # 初始化状态机
    current_state = "WAITING_FOR_GAME"
    lcu_port, lcu_token = None, None

    print("高级数据采集程序已启动...")
    print("--------------------------------------------------")

    while True:
        if current_state == "WAITING_FOR_GAME":
            print("状态: [等待游戏开始] - 正在扫描游戏进程...")
            try:
                # 尝试连接游戏内API
                response = session.get(LIVE_DATA_URL, timeout=2)
                if response.status_code == 200:
                    print("检测到游戏已开始！切换到 [游戏中] 状态。")
                    # 为新游戏创建独立的文件夹
                    create_game_directories()
                    current_state = "IN_GAME"
                    # 采集第一帧数据
                    save_data_to_json(response.json(), 'live')
            except requests.exceptions.RequestException:
                # 游戏未开始，继续等待
                pass

        elif current_state == "IN_GAME":
            print("状态: [游戏中] - 正在采集中...")
            try:
                # 持续采集实时数据
                response = session.get(LIVE_DATA_URL, timeout=2)
                if response.status_code == 200:
                    save_data_to_json(response.json(), 'live')
            except requests.exceptions.RequestException:
                # 连接失败，意味着游戏结束
                print("游戏结束！切换到 [等待结算页面] 状态。")
                current_state = "WAITING_FOR_EOG"
                # 尝试立即获取LCU凭证
                lcu_port, lcu_token = get_lcu_credentials()

        elif current_state == "WAITING_FOR_EOG":
            print("状态: [等待结算页面] - 正在扫描客户端...")
            
            # 记录等待开始时间
            if not hasattr(main, 'eog_wait_start'):
                main.eog_wait_start = time.time()
                main.attempts = 0
            
            # 检查是否超时
            if (time.time() - main.eog_wait_start) > MAX_EOG_WAIT_TIME:
                print(f"等待结算数据超时({MAX_EOG_WAIT_TIME}秒)，重置状态，等待下一局游戏。")
                print("--------------------------------------------------")
                current_state = "WAITING_FOR_GAME"
                # 重置等待时间和尝试次数
                if hasattr(main, 'eog_wait_start'):
                    delattr(main, 'eog_wait_start')
                    delattr(main, 'attempts')
                continue
                
            # 检查凭证是否有效，如果无效则重新获取
            connection_valid = False
            
            if lcu_port and lcu_token:
                # 如果已有凭证，先测试连接
                connection_valid = test_lcu_connection(lcu_port, lcu_token)
            
            if not connection_valid:
                print("需要获取新的LCU凭证...")
                # 如果没有凭证或连接无效，则尝试获取
                lcu_port, lcu_token = get_lcu_credentials()
                
                # 测试新获取的凭证
                if lcu_port and lcu_token:
                    connection_valid = test_lcu_connection(lcu_port, lcu_token)
                    
                if not connection_valid:
                    print("错误: 未能连接到英雄联盟客户端。请确保客户端正在运行。")
                    print("将在下一轮尝试重新连接...")
                    # 短暂休眠，减少CPU使用率
                    time.sleep(1)
                else:
                    print(f"成功连接到客户端(端口:{lcu_port})，准备抓取赛后数据。")

            if connection_valid:
                # 尝试所有可能的端点
                data_found = False
                main.attempts += 1
                print(f"尝试获取结算数据 (第{main.attempts}次尝试)...")
                
                for endpoint in LCU_EOG_ENDPOINTS:
                    try:
                        # 构建LCU API的请求
                        eog_url = f"https://127.0.0.1:{lcu_port}{endpoint}"
                        auth = requests.auth.HTTPBasicAuth('riot', lcu_token)
                        
                        print(f"  尝试端点: {endpoint}")
                        # 请求赛后数据，增加超时时间
                        response = session.get(eog_url, auth=auth, timeout=10)
                        
                        # 打印响应状态和长度
                        content_length = len(response.content) if response.content else 0
                        print(f"  响应状态码: {response.status_code}, 数据长度: {content_length} 字节")

                        if response.status_code == 200 and content_length > 50:  # 确保有意义的数据
                            try:
                                # 尝试解析JSON
                                json_data = response.json()
                                # 成功获取赛后数据！
                                save_data_to_json(json_data, 'postgame')
                                print(f"成功从端点 {endpoint} 抓取赛后数据！重置状态，等待下一局游戏。")
                                print("--------------------------------------------------")
                                current_state = "WAITING_FOR_GAME"
                                # 重置凭证，因为客户端可能会重启
                                lcu_port, lcu_token = None, None
                                # 重置等待时间和尝试次数
                                if hasattr(main, 'eog_wait_start'):
                                    delattr(main, 'eog_wait_start')
                                    delattr(main, 'attempts')
                                data_found = True
                                break
                            except json.JSONDecodeError as e:
                                print(f"  JSON解析错误: {e}")
                                print("  返回的内容不是有效的JSON格式，跳过。")
                                continue
                    except requests.exceptions.ConnectionError as e:
                        print(f"  连接错误: {str(e)}")
                        # 连接错误可能意味着客户端已关闭或端口已变更
                        connection_valid = False
                        break
                    except requests.exceptions.Timeout as e:
                        print(f"  请求超时: {str(e)}")
                        # 继续尝试其他端点
                        continue
                    except requests.exceptions.RequestException as e:
                        print(f"  请求失败: {str(e)}")
                        continue
                    except Exception as e:
                        print(f"  发生未知错误: {str(e)}")
                        continue
                
                if not data_found and connection_valid:
                    print("本次尝试未获取到结算数据，将继续等待...")
                    # 继续等待，下一轮再试
                elif not connection_valid:
                    print("连接已失效，下次轮询将重新获取凭证。")
                    # 重置凭证
                    lcu_port, lcu_token = None, None

        # 轮询延时
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
    # print(get_lcu_credentials())
