"""
游戏数据采集工具 - 主界面
"""

import sys
import os
import time
import datetime
import traceback
import json
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QFileDialog, QComboBox, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont

# 导入工具函数
from utils.data_handler import DataHandler
from utils.log_uploader import upload_game_logs_manually
from utils.game_monitor import main_loop
from config import *

# 添加一个游戏监控线程类
class GameMonitorThread(QThread):
    """游戏监控后台线程"""
    update_signal = pyqtSignal(str)  # 用于发送监控状态更新的信号
    error_signal = pyqtSignal(str)   # 用于发送错误信息的信号
    finished_signal = pyqtSignal()   # 用于通知线程已结束的信号
    
    def __init__(self):
        super().__init__()
        self.running = False
        
    def run(self):
        """线程运行函数"""
        self.running = True
        self.update_signal.emit("监控已启动，正在等待游戏...")
        try:
            # 使用自定义的main_loop_ui函数代替main_loop
            self.main_loop_ui()
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
        self.running = False
        self.update_signal.emit("监控已停止")
    
    def main_loop_ui(self):
        """修改版的main_loop函数，适用于UI界面"""
        # 初始化数据处理器
        data_handler = DataHandler(LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME)
        data_handler.setup_directories()
        
        # 初始化API客户端
        from utils.api_client import ApiClient
        api_client = ApiClient(LIVE_DATA_URL, LCU_EOG_ENDPOINT)
        
        # 初始化状态机
        current_state = "WAITING_FOR_GAME"

        self.update_signal.emit("高级数据采集程序已启动...")

        while self.running:  # 使用self.running来控制循环
            if current_state == "WAITING_FOR_GAME":
                self.update_signal.emit("状态: [等待游戏开始] - 正在扫描游戏进程...")
                success, data_or_error = api_client.get_live_game_data()
                
                if success:
                    self.update_signal.emit("检测到游戏已开始！切换到 [游戏中] 状态。")
                    # 为新游戏创建独立的文件夹
                    data_handler.create_game_directories()
                    current_state = "IN_GAME"
                    # 采集第一帧数据
                    data_handler.save_data_to_json(data_or_error, 'live')

            elif current_state == "IN_GAME":
                self.update_signal.emit("状态: [游戏中] - 正在采集中...")
                success, data_or_error = api_client.get_live_game_data()
                
                if success:
                    data_handler.save_data_to_json(data_or_error, 'live')
                else:
                    # 连接失败，意味着游戏结束
                    self.update_signal.emit("游戏结束！切换到 [等待结算页面] 状态。")
                    current_state = "WAITING_FOR_EOG"
                    
            elif current_state == "WAITING_FOR_EOG":
                self.update_signal.emit("状态: [等待结算页面] - 尝试获取赛后数据...")
                
                try:
                    # 尝试获取LCU连接
                    from utils.lcu_credentials import get_lcu_credentials
                    lcu_port, lcu_token = get_lcu_credentials()
                    
                    if lcu_port and lcu_token:
                        self.update_signal.emit(f"获取到LCU凭证: 端口={lcu_port}")
                        
                        # 设置LCU凭证
                        api_client.set_lcu_credentials(lcu_port, lcu_token)
                        
                        # 尝试获取赛后数据
                        self.update_signal.emit("正在请求赛后数据...")
                        success, eog_data = api_client.get_end_of_game_data()
                        
                        if success:
                            self.update_signal.emit("已获取赛后数据！保存中...")
                            data_handler.save_data_to_json(eog_data, 'postgame')
                            self.update_signal.emit("赛后数据已保存，切换到 [等待游戏] 状态。")
                            current_state = "WAITING_FOR_GAME"
                        else:
                            self.update_signal.emit(f"获取赛后数据失败: {eog_data}")
                    else:
                        self.update_signal.emit("未能获取LCU凭证，继续尝试...")
                except Exception as e:
                    self.update_signal.emit(f"获取赛后数据时出错: {str(e)}")
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"错误详情: {error_trace}")
                
            # 暂停一段时间再继续
            time.sleep(5)
            
        self.update_signal.emit("监控已停止")

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("英雄联盟游戏数据采集工具")
        self.setMinimumSize(800, 600)
        
        # 创建中央部件和主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 初始化界面组件
        self.init_ui()
        
        # 初始化游戏监控线程
        self.monitor_thread = None
        
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
        self.init_monitor_tab()  # 游戏监控标签页
        self.init_logs_tab()     # 日志管理标签页
        self.init_settings_tab() # 设置标签页
        
        # 使用状态栏
        self.statusBar().showMessage("就绪")
        
    def init_monitor_tab(self):
        """初始化游戏监控标签页"""
        monitor_tab = QWidget()
        layout = QVBoxLayout(monitor_tab)
        
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
        
        # 初始化监控线程
        self.monitor_thread = None
        
        # 将标签页添加到标签页组件
        self.tab_widget.addTab(monitor_tab, "游戏监控")
        
    def init_logs_tab(self):
        """初始化日志管理标签页"""
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        
        # 日志选择器
        selector_layout = QHBoxLayout()
        selector_label = QLabel("选择游戏:")
        self.game_selector = QComboBox()
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_game_list)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.game_selector)
        selector_layout.addWidget(self.refresh_button)
        layout.addLayout(selector_layout)
        
        # 日志文件列表
        layout.addWidget(QLabel("日志文件列表:"))
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["文件名", "大小", "时间"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.log_table.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.log_table.setAlternatingRowColors(True)  # 设置交替行颜色
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为不可编辑
        self.log_table.setMinimumHeight(300)  # 设置最小高度
        layout.addWidget(self.log_table)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("上传选中文件")
        self.view_button = QPushButton("查看文件内容")
        self.export_button = QPushButton("导出文件")
        
        # 连接按钮点击事件
        self.upload_button.clicked.connect(self.upload_selected_log)
        self.view_button.clicked.connect(self.view_log_content)
        self.export_button.clicked.connect(self.export_log_file)
        
        # 初始状态下禁用按钮，需要选择日志文件后才启用
        self.upload_button.setEnabled(False)
        self.view_button.setEnabled(False)
        self.export_button.setEnabled(False)
        
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.view_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)
        
        # 连接选择变化信号
        self.game_selector.currentIndexChanged.connect(self.on_game_selected)
        self.log_table.itemSelectionChanged.connect(self.on_log_selection_changed)
        
        # 将标签页添加到标签页组件
        self.tab_widget.addTab(logs_tab, "日志管理")
        
        # 初始化加载游戏列表
        self.refresh_game_list()
        
    def init_settings_tab(self):
        """初始化设置标签页"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # TODO: 添加设置项
        
        # 将标签页添加到标签页组件
        self.tab_widget.addTab(settings_tab, "设置")
    
    def start_monitoring(self):
        """开始监控游戏"""
        if not self.monitor_thread or not self.monitor_thread.running:
            # 清空现有日志
            while self.log_text.rowCount() > 0:
                self.log_text.removeRow(0)
                
            # 创建并启动监控线程
            self.monitor_thread = GameMonitorThread()
            self.monitor_thread.update_signal.connect(self.update_monitoring_log)
            self.monitor_thread.error_signal.connect(self.handle_monitoring_error)
            self.monitor_thread.finished_signal.connect(self.handle_monitoring_finished)
            self.monitor_thread.start()
            
            # 更新界面状态
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("当前状态: 监控中")
            self.statusBar().showMessage("游戏监控已启动")
            
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
        self.statusBar().showMessage(f"监控更新: {message}")
    
    def handle_monitoring_error(self, error_message):
        """处理监控错误"""
        # 显示错误消息框
        QMessageBox.critical(self, "监控错误", f"监控过程中发生错误:\n{error_message}")
        
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
        self.statusBar().showMessage("监控已停止")
    
    # 以下是日志管理标签页相关的方法
    def refresh_game_list(self):
        """刷新游戏列表"""
        self.statusBar().showMessage("正在加载游戏列表...")
        self.game_selector.clear()
        
        # 获取所有游戏文件夹
        live_dir = LOG_DIR_BASE_LIVE
        postgame_dir = LOG_DIR_BASE_POSTGAME
        
        live_folders = []
        if os.path.exists(live_dir):
            live_folders = [f for f in os.listdir(live_dir) if os.path.isdir(os.path.join(live_dir, f))]
        
        postgame_folders = []
        if os.path.exists(postgame_dir):
            postgame_folders = [f for f in os.listdir(postgame_dir) if os.path.isdir(os.path.join(postgame_dir, f))]
        
        # 合并并去重
        all_folders = sorted(list(set(live_folders + postgame_folders)), reverse=True)  # 最新的游戏在前面
        
        if not all_folders:
            self.game_selector.addItem("未找到游戏记录")
            self.statusBar().showMessage("未找到任何游戏记录")
            return
        
        for folder in all_folders:
            # 尝试将时间戳格式化为更友好的显示
            try:
                timestamp = datetime.datetime.strptime(folder, "%Y-%m-%d_%H-%M-%S")
                display_text = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                self.game_selector.addItem(display_text, folder)  # 显示文本，实际值
            except ValueError:
                # 如果不是标准时间戳格式，直接使用文件夹名
                self.game_selector.addItem(folder, folder)
        
        self.statusBar().showMessage(f"找到 {len(all_folders)} 个游戏记录")
    
    def on_game_selected(self, index):
        """当选择游戏时触发"""
        if index < 0:
            return
        
        # 清空日志文件表格
        self.log_table.setRowCount(0)
        
        # 获取选中的游戏文件夹
        folder = self.game_selector.itemData(index)
        if folder is None:
            return
        
        self.statusBar().showMessage(f"正在加载游戏 {folder} 的日志文件...")
        
        # 查找该游戏的所有日志文件
        log_files = []
        
        # 检查实时数据日志
        live_path = os.path.join(LOG_DIR_BASE_LIVE, folder)
        if os.path.exists(live_path):
            for file in os.listdir(live_path):
                if file.endswith('.json'):
                    full_path = os.path.join(live_path, file)
                    size = os.path.getsize(full_path)
                    time_str = os.path.getmtime(full_path)
                    log_files.append({
                        'name': file,
                        'path': full_path,
                        'size': size,
                        'time': time_str,
                        'type': 'live'
                    })
        
        # 检查赛后数据日志
        postgame_path = os.path.join(LOG_DIR_BASE_POSTGAME, folder)
        if os.path.exists(postgame_path):
            for file in os.listdir(postgame_path):
                if file.endswith('.json'):
                    full_path = os.path.join(postgame_path, file)
                    size = os.path.getsize(full_path)
                    time_str = os.path.getmtime(full_path)
                    log_files.append({
                        'name': file,
                        'path': full_path,
                        'size': size,
                        'time': time_str,
                        'type': 'postgame'
                    })
        
        # 按时间排序
        log_files.sort(key=lambda x: x['time'], reverse=True)
        
        # 添加到表格
        for log_file in log_files:
            row_position = self.log_table.rowCount()
            self.log_table.insertRow(row_position)
            
            # 文件名 (带类型标记)
            file_name = f"[{log_file['type']}] {log_file['name']}"
            self.log_table.setItem(row_position, 0, QTableWidgetItem(file_name))
            
            # 文件大小
            size_str = self.format_size(log_file['size'])
            self.log_table.setItem(row_position, 1, QTableWidgetItem(size_str))
            
            # 文件时间
            time_obj = datetime.datetime.fromtimestamp(log_file['time'])
            time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            self.log_table.setItem(row_position, 2, QTableWidgetItem(time_str))
            
            # 存储完整路径到第一列的数据中
            self.log_table.item(row_position, 0).setData(Qt.UserRole, log_file['path'])
        
        self.statusBar().showMessage(f"已加载 {len(log_files)} 个日志文件")
    
    def on_log_selection_changed(self):
        """当日志文件选择变化时触发"""
        selected_items = self.log_table.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.upload_button.setEnabled(has_selection)
        self.view_button.setEnabled(has_selection)
        self.export_button.setEnabled(has_selection)
    
    def get_selected_log_path(self):
        """获取当前选中的日志文件路径"""
        selected_rows = self.log_table.selectionModel().selectedRows()
        if not selected_rows:
            selected_items = self.log_table.selectedItems()
            if not selected_items:
                return None
            selected_row = selected_items[0].row()
        else:
            selected_row = selected_rows[0].row()
        
        # 从数据中获取完整路径
        return self.log_table.item(selected_row, 0).data(Qt.UserRole)
    
    def upload_selected_log(self):
        """上传选中的日志文件"""
        log_path = self.get_selected_log_path()
        if not log_path:
            QMessageBox.warning(self, "上传错误", "请先选择一个日志文件")
            return
        
        try:
            # 创建数据处理器
            data_handler = DataHandler(LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME)
            
            # 上传文件
            from config import LOG_SERVER_URL
            self.statusBar().showMessage(f"正在上传 {os.path.basename(log_path)}...")
            success, response = data_handler.upload_log_file(log_path, LOG_SERVER_URL)
            
            if success:
                QMessageBox.information(self, "上传成功", f"文件已成功上传\n\n服务器响应: {response}")
                self.statusBar().showMessage("日志文件上传成功")
            else:
                QMessageBox.warning(self, "上传失败", f"上传过程中出错:\n{response}")
                self.statusBar().showMessage("日志文件上传失败")
        except Exception as e:
            QMessageBox.critical(self, "上传错误", f"上传过程中发生异常:\n{str(e)}")
            self.statusBar().showMessage(f"上传出错: {str(e)}")
            
    def view_log_content(self):
        """查看日志文件内容"""
        log_path = self.get_selected_log_path()
        if not log_path:
            QMessageBox.warning(self, "查看错误", "请先选择一个日志文件")
            return
        
        try:
            # 读取JSON文件内容
            with open(log_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 格式化JSON显示
            json_text = json.dumps(json_data, indent=4, ensure_ascii=False)
            
            # 创建查看窗口
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
            dialog = QDialog(self)
            dialog.setWindowTitle(f"查看文件内容 - {os.path.basename(log_path)}")
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout(dialog)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(json_text)
            layout.addWidget(text_edit)
            
            dialog.exec_()
            
        except json.JSONDecodeError:
            QMessageBox.warning(self, "格式错误", "文件不是有效的JSON格式")
        except Exception as e:
            QMessageBox.critical(self, "查看错误", f"查看文件内容时发生异常:\n{str(e)}")
    
    def export_log_file(self):
        """导出日志文件到指定位置"""
        log_path = self.get_selected_log_path()
        if not log_path:
            QMessageBox.warning(self, "导出错误", "请先选择一个日志文件")
            return
        
        # 使用文件保存对话框
        save_path, _ = QFileDialog.getSaveFileName(
            self, "导出日志文件", 
            os.path.basename(log_path), 
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if not save_path:  # 用户取消
            return
        
        try:
            # 复制文件
            import shutil
            shutil.copy2(log_path, save_path)
            QMessageBox.information(self, "导出成功", f"文件已成功导出到:\n{save_path}")
            self.statusBar().showMessage(f"文件已导出至 {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出文件时发生异常:\n{str(e)}")
            self.statusBar().showMessage(f"导出失败: {str(e)}")
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

# 主函数
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
