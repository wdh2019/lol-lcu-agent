"""
测试脚本 - 工具函数测试
这个脚本用于测试各个工具函数，便于调试
"""
import sys
import os
import argparse
# 添加项目根目录到路径，以便能够导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.api_client import ApiClient
from src.utils.data_handler import DataHandler
from src.utils.lcu_credentials import get_lcu_credentials, test_lcu_connection
from src.utils.system_utils import list_running_processes
from src.config import *

def test_api_client():
    """测试API客户端"""
    print("测试API客户端...")
    api_client = ApiClient()
    success, data = api_client.get_live_game_data()
    if success:
        print("成功获取游戏数据")
        print(f"数据示例: {str(data)[:200]}...")
    else:
        print(f"获取游戏数据失败: {data}")

def test_lcu_credentials():
    """测试LCU凭证获取"""
    print("测试LCU凭证获取...")
    port, token = get_lcu_credentials()
    if port and token:
        print(f"成功获取LCU凭证: 端口={port}")
        # 测试连接
        api_client = ApiClient()
        api_client.set_lcu_credentials(port, token)
        print("尝试获取赛后数据...")
        success, data, _ = api_client.get_postgame_data(port, token)
        if success:
            print("成功获取赛后数据")
            print(f"数据示例: {str(data)[:200]}...")
        else:
            print(f"获取赛后数据失败: {data}")
    else:
        print("获取LCU凭证失败，请确保英雄联盟客户端正在运行")

def test_data_handler():
    """测试数据处理器"""
    print("测试数据处理器...")
    data_handler = DataHandler(LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME)
    data_handler.setup_directories()
    print(f"日志目录已设置: {LOG_DIR_BASE_LIVE}, {LOG_DIR_BASE_POSTGAME}")
    
    # 列出所有游戏日志
    print("检测到的游戏日志文件夹:")
    live_folders = []
    if os.path.exists(LOG_DIR_BASE_LIVE):
        live_folders = [f for f in os.listdir(LOG_DIR_BASE_LIVE) if os.path.isdir(os.path.join(LOG_DIR_BASE_LIVE, f))]
        for folder in live_folders:
            print(f"- {folder} (实时)")
    
    postgame_folders = []
    if os.path.exists(LOG_DIR_BASE_POSTGAME):
        postgame_folders = [f for f in os.listdir(LOG_DIR_BASE_POSTGAME) if os.path.isdir(os.path.join(LOG_DIR_BASE_POSTGAME, f))]
        for folder in postgame_folders:
            print(f"- {folder} (赛后)")
    
    if not live_folders and not postgame_folders:
        print("没有找到任何游戏日志")

def test_system_utils():
    """测试系统工具"""
    print("测试系统工具...")
    print("列出当前运行的游戏相关进程:")
    list_running_processes()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试工具函数")
    parser.add_argument("--api", action="store_true", help="测试API客户端")
    parser.add_argument("--lcu", action="store_true", help="测试LCU凭证获取")
    parser.add_argument("--data", action="store_true", help="测试数据处理器")
    parser.add_argument("--sys", action="store_true", help="测试系统工具")
    parser.add_argument("--all", action="store_true", help="测试所有功能")
    
    args = parser.parse_args()
    
    if args.api or args.all:
        test_api_client()
        print()
    
    if args.lcu or args.all:
        test_lcu_credentials()
        print()
    
    if args.data or args.all:
        test_data_handler()
        print()
    
    if args.sys or args.all:
        test_system_utils()
        print()
    
    if not (args.api or args.lcu or args.data or args.sys or args.all):
        parser.print_help()
