"""
UI组件基类
包含共享属性和方法
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt

# 导入单例日志管理器
from ..utils.log_manager import get_logger

class BaseTab(QWidget):
    """标签页基类"""
    
    def __init__(self, parent=None):
        """
        初始化基础标签页
        
        参数:
            parent: 父窗口实例，通常是MainWindow
        """
        super().__init__()
        self.main_window = parent
        self.config_manager = parent.config_manager if parent else None
        
        # 使用单例日志管理器，无需通过参数传递
        self.log_manager = get_logger()
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面，子类必须重写此方法"""
        raise NotImplementedError("子类必须实现init_ui方法")
        
    def get_config(self, key, default=None):
        """获取配置项"""
        if self.config_manager:
            return self.config_manager.current_config.get(key, default)
        return default
    
    def show_message(self, title, message):
        """显示消息对话框"""
        self.log_manager.info(f"消息对话框: {title} - {message}")
        QMessageBox.information(self, title, message)
        
    def show_error(self, title, message):
        """显示错误对话框"""
        self.log_manager.error(f"错误对话框: {title} - {message}")
        QMessageBox.critical(self, title, message)
        
    def show_warning(self, title, message):
        """显示警告对话框"""
        self.log_manager.warning(f"警告对话框: {title} - {message}")
        QMessageBox.warning(self, title, message)
        
    def show_question(self, title, message):
        """显示确认对话框"""
        self.log_manager.info(f"确认对话框: {title} - {message}")
        reply = QMessageBox.question(self, title, message, 
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        result = reply == QMessageBox.Yes
        self.log_manager.info(f"确认对话框结果: {'是' if result else '否'}")
        return result
        
    def update_status(self, message):
        """更新状态栏消息"""
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message)
        self.log_manager.debug(f"状态栏: {message}")
        
    def log_info(self, message):
        """记录信息日志"""
        self.log_manager.info(message)
        
    def log_error(self, message):
        """记录错误日志"""
        self.log_manager.error(message)
        
    def log_warning(self, message):
        """记录警告日志"""
        self.log_manager.warning(message)
        
    def log_debug(self, message):
        """记录调试日志"""
        self.log_manager.debug(message)
