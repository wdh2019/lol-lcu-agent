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
            config_module: 包含配置项的模块
        """
        self.config_module = config_module
        self.original_config = {}
        self.current_config = {}
        self.load_config()
    
    def load_config(self):
        """从配置模块加载配置到字典中"""
        import inspect
        
        # 获取所有不以下划线开头的变量
        for name, value in inspect.getmembers(self.config_module):
            if not name.startswith('_') and not inspect.ismodule(value) and not inspect.isfunction(value):
                self.original_config[name] = value
        
        # 创建当前配置的副本
        self.current_config = copy.deepcopy(self.original_config)
        
        return self.current_config
    
    def save_config(self, new_config):
        """
        保存配置到模块中
        
        参数:
            new_config: 包含新配置值的字典
        """
        # 更新当前配置
        self.current_config.update(new_config)
        
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
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(config_content))
        
        # 重新加载配置模块
        import importlib
        importlib.reload(self.config_module)
        
        # 重新加载配置字典
        self.load_config()
        
        return True
