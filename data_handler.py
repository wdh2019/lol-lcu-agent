import os
import json
import time

class DataHandler:
    """处理数据保存和目录管理的类"""
    
    def __init__(self, live_dir="game_logs_live", postgame_dir="game_logs_postgame"):
        """
        初始化数据处理器
        
        参数:
            live_dir: 实时游戏数据的目录
            postgame_dir: 赛后数据的目录
        """
        self.log_dir_base_live = live_dir
        self.log_dir_base_postgame = postgame_dir
        self.current_game_log_dir_live = ""
        self.current_game_log_dir_postgame = ""
        
    def setup_directories(self):
        """检查并创建用于存放日志的文件夹"""
        for dir_name in [self.log_dir_base_live, self.log_dir_base_postgame]:
            if not os.path.exists(dir_name):
                print(f"基础日志文件夹 '{dir_name}' 不存在，正在创建...")
                os.makedirs(dir_name)
                
    def create_game_directories(self):
        """为当前游戏创建一个新的文件夹，用时间戳命名"""
        # 生成当前时间戳作为文件夹名
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        
        # 为当前游戏创建新的文件夹
        self.current_game_log_dir_live = os.path.join(self.log_dir_base_live, timestamp)
        self.current_game_log_dir_postgame = os.path.join(self.log_dir_base_postgame, timestamp)
        
        # 创建文件夹
        os.makedirs(self.current_game_log_dir_live, exist_ok=True)
        os.makedirs(self.current_game_log_dir_postgame, exist_ok=True)
        
        print(f"已为当前游戏创建新的数据文件夹: {timestamp}")
        
    def save_data_to_json(self, data, data_type):
        """将获取到的数据保存为格式化的JSON文件"""
        # 使用当前游戏的日志文件夹
        log_dir = self.current_game_log_dir_live if data_type == 'live' else self.current_game_log_dir_postgame
        try:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(log_dir, f"data_{timestamp}.json")

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(f"[{time.strftime('%H:%M:%S')}] 成功获取 [{data_type}] 数据并保存到: {filename}")

        except Exception as e:
            print(f"保存文件时出错: {e}")
