"""
日志记录工具
提供统一的日志记录功能，支持控制台输出和文件记录
采用单例模式，确保整个项目只有一个日志管理器实例
"""
import os
import sys
import logging
import traceback
from datetime import datetime

class LogManager:
    """日志管理器，提供统一的日志记录接口（单例模式）"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, log_dir=None, log_level=logging.INFO, console_output=True):
        """单例模式实现，确保只有一个实例"""
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir=None, log_level=logging.INFO, console_output=True):
        """
        初始化日志管理器（只初始化一次）
        
        参数:
            log_dir: 日志文件保存目录，如果为None则使用默认目录
            log_level: 日志级别，默认为INFO
            console_output: 是否同时输出到控制台
        """
        # 如果已经初始化过，直接返回
        if LogManager._initialized:
            return
            
        # 设置日志目录
        if log_dir is None:
            # 默认日志目录在用户文档下的LoL-Data-Collector/logs
            self.log_dir = os.path.join(os.path.expanduser("~"), "Documents", "LoL-Data-Collector", "logs")
        else:
            self.log_dir = log_dir
            
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建logger对象
        self.logger = logging.getLogger('lcu_agent')
        self.logger.setLevel(log_level)
        self.logger.propagate = False  # 避免日志重复
        
        # 清除可能存在的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建日志文件名，格式为：程序名_日期_时间.log
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"lcu_agent_{current_datetime}.log"
        log_filepath = os.path.join(self.log_dir, log_filename)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # 设置日志格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        # 添加到logger
        self.logger.addHandler(file_handler)
        
        # 如果需要控制台输出，添加控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        self.log_filepath = log_filepath
        
        # 记录启动信息
        self.logger.info("="*50)
        self.logger.info("日志系统已初始化")
        self.logger.info(f"日志文件路径: {log_filepath}")
        self.logger.info(f"日志级别: {logging.getLevelName(log_level)}")
        self.logger.info("="*50)
        
        # 标记为已初始化
        LogManager._initialized = True
        
    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=None):
        """
        记录错误信息
        
        参数:
            message: 错误消息
            exc_info: 异常信息，如果为None但有异常发生，会自动获取
        """
        if exc_info is None and sys.exc_info()[0] is not None:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)
    
    def critical(self, message, exc_info=None):
        """
        记录严重错误信息
        
        参数:
            message: 错误消息
            exc_info: 异常信息，如果为None但有异常发生，会自动获取
        """
        if exc_info is None and sys.exc_info()[0] is not None:
            self.logger.critical(message, exc_info=True)
        else:
            self.logger.critical(message)
    
    def get_log_filepath(self):
        """获取当前日志文件路径"""
        return self.log_filepath
    
    def close_handlers(self):
        """关闭所有日志处理器"""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def init_handlers(self):
        """重新初始化日志处理器（在清空日志后调用）"""
        # 清除现有处理器
        self.close_handlers()
        
        # 创建新的日志文件名，格式为：程序名_日期_时间.log
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"lcu_agent_{current_datetime}.log"
        log_filepath = os.path.join(self.log_dir, log_filename)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(self.logger.level)
        
        # 设置日志格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        # 添加到logger
        self.logger.addHandler(file_handler)
        
        # 添加控制台处理器（如果之前有的话）
        has_console_handler = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) 
                                 for h in self.logger.handlers)
        if not has_console_handler:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.logger.level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        self.log_filepath = log_filepath
        self.logger.info("日志处理器已重新初始化")
        self.logger.info(f"新日志文件路径: {log_filepath}")
        
    def set_exception_hook(self):
        """设置全局异常处理钩子，捕获未处理的异常"""
        original_hook = sys.excepthook
        
        def exception_hook(exc_type, exc_value, exc_traceback):
            # 记录未捕获的异常
            self.critical("发生未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
            # 仍然调用原始的异常处理
            return original_hook(exc_type, exc_value, exc_traceback)
            
        sys.excepthook = exception_hook
    
    def cleanup_old_logs(self, max_age_days=30):
        """
        清理旧的日志文件
        
        参数:
            max_age_days: 日志文件保留的最大天数，默认为30天
        
        返回:
            元组 (删除的文件数量, 删除的总字节数)
        """
        import time
        from datetime import datetime, timedelta
        
        # 获取当前时间
        now = time.time()
        # 计算截止日期的时间戳（当前时间减去max_age_days天）
        cutoff = now - (max_age_days * 24 * 60 * 60)
        
        # 统计信息
        deleted_count = 0
        deleted_size = 0
        
        try:
            # 确保日志目录存在
            if not os.path.exists(self.log_dir):
                return (0, 0)
                
            # 获取日志目录中所有的.log文件
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
            
            # 检查每个文件
            for log_file in log_files:
                file_path = os.path.join(self.log_dir, log_file)
                
                # 获取文件的最后修改时间
                file_mtime = os.path.getmtime(file_path)
                
                # 如果文件早于截止日期，则删除
                if file_mtime < cutoff:
                    # 获取文件大小
                    file_size = os.path.getsize(file_path)
                    
                    # 删除文件
                    os.remove(file_path)
                    
                    # 更新统计信息
                    deleted_count += 1
                    deleted_size += file_size
                    
                    self.logger.debug(f"已删除过期日志文件: {log_file}")
            
            if deleted_count > 0:
                self.logger.info(f"已清理 {deleted_count} 个过期日志文件，释放 {self._format_size(deleted_size)} 空间")
                
            return (deleted_count, deleted_size)
            
        except Exception as e:
            self.logger.error(f"清理旧日志文件时出错: {str(e)}")
            return (0, 0)
    
    def _format_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    @classmethod
    def get_instance(cls):
        """获取单例实例的类方法"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """重置单例实例（主要用于测试或重新配置）"""
        if cls._instance is not None:
            # 关闭现有的日志处理器
            cls._instance.close_handlers()
        cls._instance = None
        cls._initialized = False


# 提供全局访问函数，方便其他模块使用
def get_logger():
    """获取全局日志管理器实例"""
    return LogManager.get_instance()


# 注意：不在这里创建默认实例，避免导入时就初始化
# 让应用程序在合适的时机使用正确的配置来初始化
