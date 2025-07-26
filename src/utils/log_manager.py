"""
日志记录工具
提供统一的日志记录功能，支持控制台输出和文件记录
"""
import os
import sys
import logging
import traceback
from datetime import datetime

class LogManager:
    """日志管理器，提供统一的日志记录接口"""
    
    def __init__(self, log_dir=None, log_level=logging.INFO, console_output=True):
        """
        初始化日志管理器
        
        参数:
            log_dir: 日志文件保存目录，如果为None则使用默认目录
            log_level: 日志级别，默认为INFO
            console_output: 是否同时输出到控制台
        """
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
        
        # 创建日志文件名，格式为：程序名_日期.log
        current_date = datetime.now().strftime('%Y%m%d')
        log_filename = f"lcu_agent_{current_date}.log"
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
        
    def set_exception_hook(self):
        """设置全局异常处理钩子，捕获未处理的异常"""
        original_hook = sys.excepthook
        
        def exception_hook(exc_type, exc_value, exc_traceback):
            # 记录未捕获的异常
            self.critical("发生未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
            # 仍然调用原始的异常处理
            return original_hook(exc_type, exc_value, exc_traceback)
            
        sys.excepthook = exception_hook
