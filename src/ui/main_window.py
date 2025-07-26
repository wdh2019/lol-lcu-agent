"""
游戏数据采集工具 - 主界面
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# 导入工具函数
from src.utils.config_manager import ConfigManager
import src.config as config_module

# 导入单例日志管理器
from ..utils.log_manager import get_logger

# 导入标签页模块
from .monitor_tab import MonitorTab
from .logs_tab import LogsTab
from .settings_tab import SettingsTab

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("英雄联盟游戏数据采集工具")
        self.setMinimumSize(800, 600)
        
        # 使用单例日志管理器
        self.log_manager = get_logger()
        self.log_manager.info("主窗口初始化")
        
        # 创建中央部件和主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 加载配置
        self.config_manager = ConfigManager(config_module)
        
        # 初始化界面组件
        self.init_ui()
        
    def init_ui(self):
        """初始化界面组件"""
        # 创建标题标签
        title_label = QLabel("英雄联盟游戏数据采集工具")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)
        
        # 创建标签页组件
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # 添加标签页
        self.monitor_tab = MonitorTab(self)
        self.logs_tab = LogsTab(self)
        self.settings_tab = SettingsTab(self)
        
        self.tab_widget.addTab(self.monitor_tab, "游戏监控")
        self.tab_widget.addTab(self.logs_tab, "游戏数据管理")
        self.tab_widget.addTab(self.settings_tab, "设置")
        
        # 使用状态栏
        self.statusBar().showMessage("就绪")

# 主函数
def main():
    """应用程序入口函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # 记录应用程序启动完成
    log_manager = get_logger()
    log_manager.info("图形界面已启动")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
