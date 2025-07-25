"""
游戏监控标签页
"""
import traceback
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

from .base_tab import BaseTab

class GameMonitorThread(QThread):
    """游戏监控后台线程"""
    update_signal = pyqtSignal(str)  # 用于发送监控状态更新的信号
    error_signal = pyqtSignal(str)   # 用于发送错误信息的信号
    finished_signal = pyqtSignal()   # 用于通知线程已结束的信号
    
    def __init__(self, config_manager=None):
        super().__init__()
        self.running = False
        self._should_stop = False  # 停止标志
        self.config_manager = config_manager
    
    def send_update(self, message):
        """发送更新信号的回调函数"""
        self.update_signal.emit(message)
    
    def should_stop(self):
        """检查是否应该停止线程"""
        return self._should_stop
    
    def run(self):
        """线程运行函数"""
        from src.utils.game_monitor import main_loop
        
        self._should_stop = False
        self.running = True
        
        try:
            # 获取最新的配置
            config_dict = {}
            if self.config_manager:
                config_dict = self.config_manager.current_config
            
            # 使用改进后的main_loop函数，传入停止检查函数和输出重定向函数
            main_loop(
                stop_check_func=self.should_stop, 
                print_func=self.send_update,
                config_dict=config_dict
            )
        except Exception as e:
            error_msg = f"监控出错: {str(e)}"
            self.update_signal.emit(error_msg)
            self.error_signal.emit(error_msg)
            # 打印详细的异常堆栈信息
            print(traceback.format_exc())
        finally:
            self.running = False
            self.finished_signal.emit()  # 无论如何，都发送结束信号
    
    def stop(self):
        """停止监控"""
        if self.running:
            self._should_stop = True
            self.update_signal.emit("正在停止监控...")

class MonitorTab(BaseTab):
    """游戏监控标签页"""
    
    def __init__(self, parent=None):
        self.monitor_thread = None
        super().__init__(parent)
    
    def init_ui(self):
        """初始化标签页界面"""
        layout = QVBoxLayout(self)
        
        # 状态显示区域
        self.status_label = QLabel("当前状态: 未监控")
        layout.addWidget(self.status_label)
        
        # 控制按钮区域
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始监控")
        self.stop_button = QPushButton("停止监控")
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)  # 初始状态下禁用停止按钮
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # 监控日志区域
        log_label = QLabel("监控日志:")
        layout.addWidget(log_label)
        
        # 添加实时日志显示组件
        self.log_text = QTableWidget()
        self.log_text.setColumnCount(2)
        self.log_text.setHorizontalHeaderLabels(["时间", "消息"])
        self.log_text.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.log_text.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.log_text.setMinimumHeight(300)  # 设置最小高度
        self.log_text.setAlternatingRowColors(True)  # 设置交替行颜色
        self.log_text.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为不可编辑
        layout.addWidget(self.log_text)
    
    def start_monitoring(self):
        """开始监控游戏"""
        if not self.monitor_thread or not self.monitor_thread.running:
            # 清空现有日志
            while self.log_text.rowCount() > 0:
                self.log_text.removeRow(0)
                
            # 创建并启动监控线程
            self.monitor_thread = GameMonitorThread(self.config_manager)
            self.monitor_thread.update_signal.connect(self.update_monitoring_log)
            self.monitor_thread.error_signal.connect(self.handle_monitoring_error)
            self.monitor_thread.finished_signal.connect(self.handle_monitoring_finished)
            self.monitor_thread.start()
            
            # 更新界面状态
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("当前状态: 监控中")
            self.update_status("游戏监控已启动")
            
            # 添加首条日志
            self.update_monitoring_log("监控已启动，等待游戏...")
    
    def stop_monitoring(self):
        """停止监控游戏"""
        if self.monitor_thread:
            # 添加日志信息
            self.update_monitoring_log("用户请求停止监控...")
            
            # 停止线程
            self.monitor_thread.stop()
            
            # 如果线程仍在运行，最多等待2秒
            if self.monitor_thread.isRunning():
                self.monitor_thread.wait(2000)
                
                # 如果仍未结束，强制终止
                if self.monitor_thread.isRunning():
                    self.update_monitoring_log("强制终止监控线程...")
                    self.monitor_thread.terminate()
                    
            # 重置界面状态
            self.reset_ui_state()
            self.update_monitoring_log("监控已停止")
    
    def update_monitoring_log(self, message):
        """更新监控日志"""
        # 更新状态标签
        self.status_label.setText(f"当前状态: {message}")
        
        # 更新日志表格
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        row_position = self.log_text.rowCount()
        self.log_text.insertRow(row_position)
        self.log_text.setItem(row_position, 0, QTableWidgetItem(current_time))
        self.log_text.setItem(row_position, 1, QTableWidgetItem(message))
        # 滚动到最新记录
        self.log_text.scrollToBottom()
        
        # 更新状态栏
        self.update_status(f"监控更新: {message}")
    
    def handle_monitoring_error(self, error_message):
        """处理监控错误"""
        # 显示错误消息框
        self.show_error("监控错误", f"监控过程中发生错误:\n{error_message}")
        
        # 重置UI状态
        self.reset_ui_state()
    
    def handle_monitoring_finished(self):
        """处理监控完成事件"""
        # 重置UI状态
        self.reset_ui_state()
        
    def reset_ui_state(self):
        """重置UI界面状态"""
        # 启用开始按钮，禁用停止按钮
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("当前状态: 未监控")
        self.update_status("监控已停止")
