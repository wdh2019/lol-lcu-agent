"""
UI组件基类
包含共享属性和方法
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt

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
        QMessageBox.information(self, title, message)
        
    def show_error(self, title, message):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)
        
    def show_warning(self, title, message):
        """显示警告对话框"""
        QMessageBox.warning(self, title, message)
        
    def show_confirm(self, title, message):
        """显示确认对话框"""
        return QMessageBox.question(
            self, title, message, 
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes
    
    def update_status(self, message):
        """更新状态栏消息"""
        if self.main_window:
            self.main_window.statusBar().showMessage(message)
