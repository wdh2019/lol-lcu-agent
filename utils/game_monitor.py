import time
import urllib3
from .api_client import ApiClient
from .lcu_credentials import get_lcu_credentials, test_lcu_connection
from .data_handler import DataHandler
from .system_utils import list_running_processes
from config import *  # 导入所有配置项

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main_loop():
    """程序主逻辑，包含状态机"""
    # 初始化数据处理器
    data_handler = DataHandler(LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME)
    data_handler.setup_directories()
    
    # 初始化API客户端
    api_client = ApiClient(LIVE_DATA_URL, LCU_EOG_ENDPOINT)
    
    # 初始化状态机
    current_state = "WAITING_FOR_GAME"
    lcu_port, lcu_token = None, None

    print("高级数据采集程序已启动...")
    print("--------------------------------------------------")

    while True:
        if current_state == "WAITING_FOR_GAME":
            print("状态: [等待游戏开始] - 正在扫描游戏进程...")
            success, data_or_error = api_client.get_live_game_data()
            
            if success:
                print("检测到游戏已开始！切换到 [游戏中] 状态。")
                # 为新游戏创建独立的文件夹
                data_handler.create_game_directories()
                current_state = "IN_GAME"
                # 采集第一帧数据
                data_handler.save_data_to_json(data_or_error, 'live')

        elif current_state == "IN_GAME":
            print("状态: [游戏中] - 正在采集中...")
            success, data_or_error = api_client.get_live_game_data()
            
            if success:
                data_handler.save_data_to_json(data_or_error, 'live')
            else:
                # 连接失败，意味着游戏结束
                print("游戏结束！切换到 [等待结算页面] 状态。")
                current_state = "WAITING_FOR_EOG"
                # 尝试立即获取LCU凭证
                lcu_port, lcu_token = get_lcu_credentials(LCU_PORT, LCU_TOKEN)

        elif current_state == "WAITING_FOR_EOG":
            print("状态: [等待结算页面] - 正在扫描客户端...")
            
            # 记录等待开始时间
            if not hasattr(main_loop, 'eog_wait_start'):
                main_loop.eog_wait_start = time.time()
                main_loop.attempts = 0
            
            # 检查是否超时
            if (time.time() - main_loop.eog_wait_start) > MAX_EOG_WAIT_TIME:
                print(f"等待结算数据超时({MAX_EOG_WAIT_TIME}秒)，重置状态，等待下一局游戏。")
                print("--------------------------------------------------")
                current_state = "WAITING_FOR_GAME"
                # 重置等待时间和尝试次数
                if hasattr(main_loop, 'eog_wait_start'):
                    delattr(main_loop, 'eog_wait_start')
                    delattr(main_loop, 'attempts')
                continue
                
            # 检查凭证是否有效，如果无效则重新获取
            connection_valid = False
            
            if not lcu_port and not lcu_token:
                # 如果没有凭证，则尝试获取
                lcu_port, lcu_token = get_lcu_credentials(LCU_PORT, LCU_TOKEN)
            
            # 如果已有凭证，先测试连接
            connection_valid = test_lcu_connection(lcu_port, lcu_token, api_client.session)
            
            if not connection_valid:
                # 如果仍然无法连接，则提供更详细的错误信息
                print("错误: 未能连接到英雄联盟客户端。请确保客户端正在运行。")
                
                # 每10次尝试(约50秒)显示一次管理员权限提示和进程列表
                if not hasattr(main_loop, 'failure_count'):
                    main_loop.failure_count = 0
                
                main_loop.failure_count += 1
                if main_loop.failure_count % 10 == 1:  # 每10次显示一次详细信息
                    print("\n【重要提示】如果客户端确实在运行，可能是由于权限问题无法获取凭证。")
                    print("请以管理员身份运行此脚本:")
                    print("1. 右键点击命令提示符(cmd)或PowerShell，选择\"以管理员身份运行\"")
                    print("2. 导航到脚本所在目录")
                    print("3. 执行命令: python main.py")
                    # 列出当前系统中的进程，帮助用户查看是否有客户端进程
                    list_running_processes()
                
                print("将在下一轮尝试重新连接...")
                # 短暂休眠，减少CPU使用率
                time.sleep(1)
            else:
                print(f"成功连接到客户端(端口:{lcu_port})，准备抓取赛后数据。")
                # 成功连接后重置失败计数
                if hasattr(main_loop, 'failure_count'):
                    delattr(main_loop, 'failure_count')
                
                # 获取结算数据
                main_loop.attempts += 1
                print(f"尝试获取结算数据 (第{main_loop.attempts}次尝试)...")
                
                success, data_or_error, content_length = api_client.get_postgame_data(lcu_port, lcu_token)
                
                if success:
                    # 成功获取赛后数据！
                    data_handler.save_data_to_json(data_or_error, 'postgame')
                    print(f"成功抓取赛后数据！")
                    
                    # 如果配置了自动上传，则上传本局游戏的所有日志
                    if UPLOAD_LOGS:
                        print("开始上传本局游戏的日志文件...")
                        success_count, failed_count = data_handler.upload_game_logs(
                            log_type='both', 
                            server_url=LOG_SERVER_URL
                        )
                        if success_count > 0:
                            print(f"成功上传 {success_count} 个日志文件")
                        if failed_count > 0:
                            print(f"警告: {failed_count} 个日志文件上传失败")
                    
                    print("重置状态，等待下一局游戏。")
                    print("--------------------------------------------------")
                    current_state = "WAITING_FOR_GAME"
                    # 重置凭证，因为客户端可能会重启
                    lcu_port, lcu_token = None, None
                    # 重置等待时间和尝试次数
                    if hasattr(main_loop, 'eog_wait_start'):
                        delattr(main_loop, 'eog_wait_start')
                        delattr(main_loop, 'attempts')
                else:
                    if "连接错误" in data_or_error:
                        # 连接错误可能意味着客户端已关闭或端口已变更
                        connection_valid = False
                        print("连接已失效，下次轮询将重新获取凭证。")
                        # 重置凭证
                        lcu_port, lcu_token = None, None
                    else:
                        print("本次尝试未获取到结算数据，将继续等待...")
                        # 继续等待，下一轮再试

        # 轮询延时
        time.sleep(POLL_INTERVAL)
