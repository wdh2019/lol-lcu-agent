import os
import time
from .data_handler import DataHandler
from config import LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME, LOG_SERVER_URL


def upload_game_logs_manually(game_folder=None):
    """
    手动上传指定游戏的日志文件
    
    参数:
        game_folder: 游戏文件夹名称，不指定则列出可用的游戏文件夹供用户选择
    """
    data_handler = DataHandler(LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME)
    
    # 如果没有指定游戏文件夹，列出可用的游戏文件夹供用户选择
    if not game_folder:
        live_folders = []
        if os.path.exists(LOG_DIR_BASE_LIVE):
            live_folders = [f for f in os.listdir(LOG_DIR_BASE_LIVE) if os.path.isdir(os.path.join(LOG_DIR_BASE_LIVE, f))]
        
        postgame_folders = []
        if os.path.exists(LOG_DIR_BASE_POSTGAME):
            postgame_folders = [f for f in os.listdir(LOG_DIR_BASE_POSTGAME) if os.path.isdir(os.path.join(LOG_DIR_BASE_POSTGAME, f))]
        
        # 合并并去重
        all_folders = sorted(list(set(live_folders + postgame_folders)))
        
        if not all_folders:
            print("错误: 没有找到任何游戏日志文件夹")
            return
        
        print("找到以下游戏日志文件夹:")
        for i, folder in enumerate(all_folders, 1):
            print(f"{i}. {folder}")
        
        try:
            choice = int(input("\n请选择要上传的游戏文件夹编号: "))
            if choice < 1 or choice > len(all_folders):
                print("无效的选择")
                return
            game_folder = all_folders[choice - 1]
        except ValueError:
            print("无效的输入")
            return
    
    # 上传选定的游戏日志
    print(f"开始上传游戏 {game_folder} 的日志...")
    success_count, failed_count = data_handler.upload_game_logs(
        game_folder_name=game_folder,
        log_type='both',
        server_url=LOG_SERVER_URL
    )
    print(f"上传完成: {success_count} 个文件成功, {failed_count} 个文件失败")
