"""
日志管理标签页
"""
import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                            QComboBox)
from PyQt5.QtCore import Qt

from .base_tab import BaseTab
from .ui_utils import format_file_size, view_json_content, export_file

class LogsTab(BaseTab):
    """日志管理标签页"""
    
    def init_ui(self):
        """初始化标签页界面"""
        layout = QVBoxLayout(self)
        
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
        
        # 初始化加载游戏列表
        self.refresh_game_list()
    
    def refresh_game_list(self):
        """刷新游戏列表"""
        self.update_status("正在加载游戏列表...")
        self.game_selector.clear()
        
        # 获取所有游戏文件夹
        current_config = self.config_manager.current_config
        live_dir = current_config.get("LOG_DIR_BASE_LIVE", "game_logs_live")
        postgame_dir = current_config.get("LOG_DIR_BASE_POSTGAME", "game_logs_postgame")
        
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
            self.update_status("未找到任何游戏记录")
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
        
        self.update_status(f"找到 {len(all_folders)} 个游戏记录")
    
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
        
        self.update_status(f"正在加载游戏 {folder} 的日志文件...")
        
        # 查找该游戏的所有日志文件
        log_files = []
        
        # 获取当前配置中的日志目录
        current_config = self.config_manager.current_config
        live_dir = current_config.get("LOG_DIR_BASE_LIVE", "game_logs_live")
        postgame_dir = current_config.get("LOG_DIR_BASE_POSTGAME", "game_logs_postgame")
        
        # 检查实时数据日志
        live_path = os.path.join(live_dir, folder)
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
        postgame_path = os.path.join(postgame_dir, folder)
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
            size_str = format_file_size(log_file['size'])
            self.log_table.setItem(row_position, 1, QTableWidgetItem(size_str))
            
            # 文件时间
            time_obj = datetime.datetime.fromtimestamp(log_file['time'])
            time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            self.log_table.setItem(row_position, 2, QTableWidgetItem(time_str))
            
            # 存储完整路径到第一列的数据中
            self.log_table.item(row_position, 0).setData(Qt.UserRole, log_file['path'])
        
        self.update_status(f"已加载 {len(log_files)} 个日志文件")
    
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
            self.show_warning("上传错误", "请先选择一个日志文件")
            return
        
        try:
            # 创建数据处理器
            from utils.data_handler import DataHandler
            from config import LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME
            
            data_handler = DataHandler(LOG_DIR_BASE_LIVE, LOG_DIR_BASE_POSTGAME)
            
            # 上传文件
            from config import LOG_SERVER_URL
            self.update_status(f"正在上传 {os.path.basename(log_path)}...")
            success, response = data_handler.upload_log_file(log_path, LOG_SERVER_URL)
            
            if success:
                self.show_message("上传成功", f"文件已成功上传\n\n服务器响应: {response}")
                self.update_status("日志文件上传成功")
            else:
                self.show_warning("上传失败", f"上传过程中出错:\n{response}")
                self.update_status("日志文件上传失败")
        except Exception as e:
            self.show_error("上传错误", f"上传过程中发生异常:\n{str(e)}")
            self.update_status(f"上传出错: {str(e)}")
            
    def view_log_content(self):
        """查看日志文件内容"""
        log_path = self.get_selected_log_path()
        if not log_path:
            self.show_warning("查看错误", "请先选择一个日志文件")
            return
        
        view_json_content(self, log_path)
    
    def export_log_file(self):
        """导出日志文件到指定位置"""
        log_path = self.get_selected_log_path()
        if not log_path:
            self.show_warning("导出错误", "请先选择一个日志文件")
            return
        
        export_file(self, log_path)
