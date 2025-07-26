"""
配置管理工具
"""
import os
import json
import copy

class ConfigManager:
    """配置管理类，负责加载和保存配置"""
    
    def __init__(self, config_module):
        """
        初始化配置管理器
        
        参数:
            config_module: 包含默认配置项的模块
        """
        self.config_module = config_module
        self.original_config = {}  # 从模块中读取的原始配置
        self.current_config = {}   # 当前使用的配置（包含从配置文件中读取的用户配置）
        self.config_file = self._get_config_file_path()
        self.load_config()
    
    def _get_config_file_path(self):
        """获取配置文件路径"""
        # 从当前配置中获取配置文件路径（如果已经定义）
        if hasattr(self.config_module, 'CONFIG_DIR') and hasattr(self.config_module, 'CONFIG_FILE'):
            config_dir = self.config_module.CONFIG_DIR
            config_file = self.config_module.CONFIG_FILE
        else:
            # 默认使用用户主目录下的.lcu-agent文件夹
            config_dir = os.path.join(os.path.expanduser("~"), ".lcu-agent")
            config_file = os.path.join(config_dir, "config.json")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        return config_file
    
    def load_config(self):
        """
        加载配置：
        1. 从配置模块加载默认配置
        2. 如果存在配置文件，从配置文件加载用户配置
        """
        import inspect
        
        # 从模块获取默认配置（所有不以下划线开头的变量）
        for name, value in inspect.getmembers(self.config_module):
            if not name.startswith('_') and not inspect.ismodule(value) and not inspect.isfunction(value):
                self.original_config[name] = value
        
        # 创建当前配置的副本
        self.current_config = copy.deepcopy(self.original_config)
        
        # 尝试从配置文件加载用户配置
        try:
            if os.path.exists(self.config_file):
                print(f"从配置文件加载用户配置: {self.config_file}")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 更新当前配置
                    self.current_config.update(user_config)
                    print("用户配置已加载")
        except Exception as e:
            print(f"加载用户配置失败: {str(e)}")
            # 加载失败时使用默认配置
        
        return self.current_config
    
    def save_config(self, new_config):
        """
        保存配置到用户配置文件
        
        参数:
            new_config: 包含新配置值的字典
        """
        # 检查是否更新了配置文件路径
        config_path_changed = False
        if 'CONFIG_DIR' in new_config or 'CONFIG_FILE' in new_config:
            config_path_changed = True
            
        # 更新当前配置
        self.current_config.update(new_config)
        
        # 如果配置文件路径已更改，更新配置文件路径
        if config_path_changed:
            self.config_file = self._get_config_file_path()
        
        try:
            # 确保配置文件所在目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            print(f"正在保存配置到: {self.config_file}")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=4, ensure_ascii=False)
            print(f"配置已成功保存")
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            raise
        
    def update_module_config(self):
        """
        更新模块中的配置（用于开发调试）
        此方法将当前配置写入模块的配置文件中
        """
        # 构建配置文件内容
        config_content = []
        config_content.append('"""')
        config_content.append('全局配置项')
        config_content.append('"""')
        config_content.append('')
        
        # 添加配置项分组
        sections = {
            '# --- Live Client Data API 配置 ---': ['LIVE_DATA_URL', 'LCU_EOG_ENDPOINT', 'LCU_PORT', 'LCU_TOKEN'],
            '# --- 日志目录配置 ---': ['LOG_DIR_BASE_LIVE', 'LOG_DIR_BASE_POSTGAME'],
            '# --- 轮询配置 ---': ['POLL_INTERVAL', 'MAX_EOG_WAIT_TIME'],
            '# --- 日志上传配置 ---': ['UPLOAD_LOGS', 'LOG_SERVER_URL']
        }
        
        # 写入各个配置项，按分组
        for section, keys in sections.items():
            config_content.append(section)
            for key in keys:
                if key in self.current_config:
                    if isinstance(self.current_config[key], str):
                        config_content.append(f'{key} = "{self.current_config[key]}"')
                    else:
                        config_content.append(f'{key} = {self.current_config[key]}')
                    
                    # 如果有注释，添加注释
                    if key == 'POLL_INTERVAL':
                        config_content[-1] += '  # 减小轮询间隔，提高响应速度'
                    elif key == 'MAX_EOG_WAIT_TIME':
                        config_content[-1] += '  # 等待2分钟'
                    elif key == 'UPLOAD_LOGS':
                        config_content[-1] += '  # 是否自动上传日志'
                    elif key == 'LOG_SERVER_URL':
                        config_content[-1] += '  # 日志上传服务器URL'
            
            config_content.append('')
        
        # 写入配置文件
        src_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(src_dir, 'config.py')
        
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(config_content))
            
            # 重新加载配置模块
            import importlib
            importlib.reload(self.config_module)
            
            return True
        except Exception as e:
            print(f"更新模块配置失败: {str(e)}")
            return False
