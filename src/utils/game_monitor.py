import time
import urllib3
from .api_client import ApiClient
from .lcu_credentials import get_lcu_credentials, test_lcu_connection
from .data_handler import DataHandler
from .system_utils import list_running_processes
from src.config import (  # 明确导入需要的配置项
    LIVE_DATA_URL,
    UPLOAD_API_URL,
    AUTO_UPLOAD_POSTGAME_DATA,
    LCU_EOG_ENDPOINT,
    POLL_INTERVAL,
    LIVE_DATA_COLLECT_INTERVAL,
    MAX_EOG_WAIT_TIME,
    LOG_DIR_BASE_LIVE,
    LOG_DIR_BASE_POSTGAME,
    LCU_PORT,
    LCU_TOKEN
)

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main_loop(stop_check_func=None, print_func=None, config_dict=None):
    """
    程序主逻辑，包含状态机
    
    参数:
        stop_check_func: 用于检查是否应该停止循环的函数，返回True时停止
        print_func: 用于替换标准print函数的回调函数
        config_dict: 配置字典，替代导入的配置项
    """
    # 如果提供了替代的print函数，则使用它
    log = print_func if print_func else print
    
    # 使用提供的配置或默认配置
    if config_dict is None:
        config_dict = {}
        
    live_data_url = config_dict.get("LIVE_DATA_URL", LIVE_DATA_URL)
    lcu_eog_endpoint = config_dict.get("LCU_EOG_ENDPOINT", LCU_EOG_ENDPOINT)
    log_dir_base_live = config_dict.get("LOG_DIR_BASE_LIVE", LOG_DIR_BASE_LIVE)
    log_dir_base_postgame = config_dict.get("LOG_DIR_BASE_POSTGAME", LOG_DIR_BASE_POSTGAME)
    poll_interval = config_dict.get("POLL_INTERVAL", POLL_INTERVAL)
    live_data_collect_interval = config_dict.get("LIVE_DATA_COLLECT_INTERVAL", LIVE_DATA_COLLECT_INTERVAL)
    max_eog_wait_time = config_dict.get("MAX_EOG_WAIT_TIME", MAX_EOG_WAIT_TIME)
    
    # 初始化数据处理器
    data_handler = DataHandler(log_dir_base_live, log_dir_base_postgame)
    data_handler.setup_directories()
    
    # 初始化API客户端
    api_client = ApiClient(live_data_url, lcu_eog_endpoint)
    
    # 初始化状态机
    current_state = "WAITING_FOR_GAME"
    lcu_port, lcu_token = None, None
    last_live_data_time = 0  # 记录上次采集实时数据的时间

    log("高级数据采集程序已启动...")
    log("--------------------------------------------------")

    while True:
        # 检查是否应该停止
        if stop_check_func and stop_check_func():
            log("监控被请求停止，正在退出...")
            break
        if current_state == "WAITING_FOR_GAME":
            log("状态: [等待游戏开始] - 正在扫描游戏进程...")
            success, data_or_error = api_client.get_live_game_data()
            
            if success:
                log("检测到游戏已开始！切换到 [游戏中] 状态。")
                # 为新游戏创建独立的文件夹
                data_handler.create_game_directories()
                current_state = "IN_GAME"
                # 采集第一帧数据
                data_handler.save_data_to_json(data_or_error, 'live')
                last_live_data_time = time.time()  # 记录第一次采集时间

        elif current_state == "IN_GAME":
            # 始终检查游戏状态，确保及时响应游戏结束
            success, data_or_error = api_client.get_live_game_data()
            
            if success:
                # 游戏仍在进行中，检查是否需要采集数据
                current_time = time.time()
                if current_time - last_live_data_time >= live_data_collect_interval:
                    log("状态: [游戏中] - 正在采集中...")
                    data_handler.save_data_to_json(data_or_error, 'live')
                    last_live_data_time = current_time  # 更新最后采集时间
            else:
                # 连接失败，意味着游戏结束
                log("游戏结束！切换到 [等待结算页面] 状态。")
                current_state = "WAITING_FOR_EOG"
                # 尝试立即获取LCU凭证
                lcu_port, lcu_token = get_lcu_credentials(LCU_PORT, LCU_TOKEN)
                last_live_data_time = 0  # 重置采集时间

        elif current_state == "WAITING_FOR_EOG":
            log("状态: [等待结算页面] - 正在扫描客户端...")
            
            # 记录等待开始时间
            if not hasattr(main_loop, 'eog_wait_start'):
                main_loop.eog_wait_start = time.time()
                main_loop.attempts = 0
            
            # 检查是否超时
            if (time.time() - main_loop.eog_wait_start) > max_eog_wait_time:
                log(f"等待结算数据超时({max_eog_wait_time}秒)，重置状态，等待下一局游戏。")
                log("--------------------------------------------------")
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
                print("正在获取LCU凭证...")
                config_lcu_port = config_dict.get("LCU_PORT", LCU_PORT)
                config_lcu_token = config_dict.get("LCU_TOKEN", LCU_TOKEN)
                lcu_port, lcu_token = get_lcu_credentials(config_lcu_port, config_lcu_token)
            
            # 如果已有凭证，先测试连接
            connection_valid = test_lcu_connection(lcu_port, lcu_token, api_client.session)
            
            if not connection_valid:
                # 如果仍然无法连接，则提供更详细的错误信息
                log("错误: 未能连接到英雄联盟客户端。请确保客户端正在运行。")
                
                # 每10次尝试(约50秒)显示一次管理员权限提示和进程列表
                if not hasattr(main_loop, 'failure_count'):
                    main_loop.failure_count = 0
                
                main_loop.failure_count += 1
                if main_loop.failure_count % 10 == 1:  # 每10次显示一次详细信息
                    log("\n【重要提示】如果客户端确实在运行，可能是由于权限问题无法获取凭证。")
                    log("请以管理员身份运行此应用")
                    # 列出当前系统中的进程，帮助用户查看是否有客户端进程
                    list_running_processes()
                
                log("将在下一轮尝试重新连接...")
                # 短暂休眠，减少CPU使用率
                time.sleep(1)
            else:
                log(f"成功连接到客户端(端口:{lcu_port})，准备抓取赛后数据。")
                # 成功连接后重置失败计数
                if hasattr(main_loop, 'failure_count'):
                    delattr(main_loop, 'failure_count')
                
                # 获取结算数据
                main_loop.attempts += 1
                log(f"尝试获取结算数据 (第{main_loop.attempts}次尝试)...")
                
                success, data_or_error, content_length = api_client.get_postgame_data(lcu_port, lcu_token)
                
                if success:
                    # 成功获取赛后数据！
                    data_handler.save_data_to_json(data_or_error, 'postgame')
                    log(f"成功抓取赛后数据！")
                    
                    # 如果配置了自动上传，则上传本局的赛后游戏数据
                    if AUTO_UPLOAD_POSTGAME_DATA:
                        log("开始上传本局游戏的数据文件...")
                        success_count, failed_count = data_handler.upload_game_logs(
                            log_type='both', 
                            server_url=UPLOAD_API_URL,
                        )
                        if success_count > 0:
                            log(f"成功上传 {success_count} 个数据文件")
                        if failed_count > 0:
                            log(f"警告: {failed_count} 个数据文件上传失败")
                    
                    log("重置状态，等待下一局游戏。")
                    log("--------------------------------------------------")
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
                        log("连接已失效，下次轮询将重新获取凭证。")
                        # 重置凭证
                        lcu_port, lcu_token = None, None
                    else:
                        log("本次尝试未获取到结算数据，将继续等待...")
                        # 继续等待，下一轮再试

        # 使用标准轮询间隔进行状态检查
        time.sleep(poll_interval)
