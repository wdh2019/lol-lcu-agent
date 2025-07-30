import os
import json
import time
import requests
import hashlib
import platform
import uuid
from pathlib import Path

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
        
    def get_machine_id(self):
        """
        生成唯一的机器码
        
        返回:
            str: 机器码字符串
        """
        try:
            # 获取机器的硬件信息
            mac_address = hex(uuid.getnode())[2:]  # MAC地址
            machine_name = platform.node()  # 计算机名
            system_info = f"{platform.system()}-{platform.machine()}"  # 系统信息
            
            # 组合信息并生成哈希
            machine_info = f"{mac_address}-{machine_name}-{system_info}"
            machine_id = hashlib.md5(machine_info.encode()).hexdigest()[:16]  # 取前16位
            
            return machine_id
        except Exception as e:
            # 如果获取失败，使用随机UUID的一部分作为备选
            return str(uuid.uuid4()).replace('-', '')[:16]
        
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
            return filename  # 返回保存的文件路径，方便后续上传

        except Exception as e:
            print(f"保存文件时出错: {e}")
            return None
            
    def upload_log_file(self, file_path, file_type, server_url="https://example.com/api/upload-logs"):
        """
        将指定的日志文件以二进制流的形式上传到服务器
        
        参数:
            file_path: 要上传的文件路径
            file_type: 文件类型，'live' 或 'postgame'
            server_url: 服务器上传接口URL
            
        返回:
            success: 布尔值，上传是否成功
            response_or_error: 成功时为服务器响应，失败时为错误信息
        """
        try:
            if not os.path.exists(file_path):
                print(f"错误: 文件 {file_path} 不存在")
                return False, f"文件不存在: {file_path}"
                
            # 准备文件和请求头
            files = {
                'file': (
                    os.path.basename(file_path),
                    open(file_path, 'rb'),
                    'application/json'
                )
            }
            
            # 准备一些元数据
            payload = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'file_type': file_type,
                'game_id': os.path.basename(os.path.dirname(file_path)),  # 使用文件夹名称作为游戏ID
                'machine_id': self.get_machine_id()  # 添加机器码
            }
            
            print(f"正在上传文件 {os.path.basename(file_path)} 到服务器...")
            response = requests.post(server_url, files=files, data=payload)
            
            # 关闭文件
            files['file'][1].close()
            
            if response.status_code == 200:
                print(f"文件 {os.path.basename(file_path)} 上传成功!")
                return True, response.json()
            else:
                print(f"上传失败，服务器返回状态码: {response.status_code}")
                return False, f"上传失败，状态码: {response.status_code}, 响应: {response.text}"
                
        except Exception as e:
            print(f"上传文件时发生错误: {e}")
            return False, f"上传错误: {str(e)}"
            
    def upload_game_logs(self, game_folder_name=None, log_type='both', server_url="https://example.com/api/upload-logs"):
        """
        上传一个游戏的所有日志文件
        
        参数:
            game_folder_name: 游戏文件夹名称，不指定则使用当前游戏
            log_type: 要上传的日志类型，'live'、'postgame'或'both'
            server_url: 服务器上传接口URL
            
        返回:
            success_count: 成功上传的文件数量
            failed_count: 上传失败的文件数量
        """
        success_count = 0
        failed_count = 0
        
        # 确定要处理的游戏文件夹
        game_folder = game_folder_name
        if not game_folder:
            # 使用当前游戏的文件夹名
            if self.current_game_log_dir_live:
                game_folder = os.path.basename(self.current_game_log_dir_live)
            else:
                print("错误: 没有指定游戏文件夹，且当前没有活动的游戏")
                return 0, 0
        
        # 确定要处理的文件夹路径
        folders_to_process = []
        if log_type in ['live', 'both']:
            folders_to_process.append((os.path.join(self.log_dir_base_live, game_folder), 'live'))
        if log_type in ['postgame', 'both']:
            folders_to_process.append((os.path.join(self.log_dir_base_postgame, game_folder), 'postgame'))
            
        # 遍历所有文件夹，上传文件
        for folder, current_file_type in folders_to_process:
            if not os.path.exists(folder):
                print(f"警告: 文件夹 {folder} 不存在，跳过")
                continue
                
            # 获取文件夹中的所有JSON文件
            json_files = [f for f in os.listdir(folder) if f.endswith('.json')]
            
            if not json_files:
                print(f"警告: 文件夹 {folder} 中没有JSON文件，跳过")
                continue
                
            print(f"开始上传文件夹 {folder} 中的 {len(json_files)} 个文件...")
            
            # 上传每个文件
            for json_file in json_files:
                file_path = os.path.join(folder, json_file)
                success, _ = self.upload_log_file(file_path, current_file_type, server_url)
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                    
        print(f"日志上传完成: {success_count} 成功, {failed_count} 失败")
        return success_count, failed_count
