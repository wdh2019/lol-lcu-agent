"""
设置标签页
"""
import os
import datetime
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QFormLayout, QGroupBox, QSpinBox,
                            QCheckBox, QComboBox)
from PyQt5.QtCore import Qt

from .base_tab import BaseTab
from .ui_utils import browse_directory, create_directory_if_not_exists, export_config_file, import_config_file

class SettingsTab(BaseTab):
    """设置标签页"""
    
    def init_ui(self):
        """初始化标签页界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 加载当前配置
        config = self.config_manager.current_config
        
        # --- LCU API 配置组 ---
        lcu_group = QGroupBox("LCU API 配置")
        lcu_form = QFormLayout()
        lcu_group.setLayout(lcu_form)
        
        self.upload_api_url = QLineEdit(config.get("UPLOAD_API_URL", ""))
        self.lcu_eog_endpoint = QLineEdit(config.get("LCU_EOG_ENDPOINT", ""))
        self.lcu_port = QLineEdit(config.get("LCU_PORT", ""))
        self.lcu_token = QLineEdit(config.get("LCU_TOKEN", ""))
        
        lcu_form.addRow("游戏数据上传接口:", self.upload_api_url)
        lcu_form.addRow("赛后数据端点:", self.lcu_eog_endpoint)
        lcu_form.addRow("LCU 端口:", self.lcu_port)
        lcu_form.addRow("LCU 令牌:", self.lcu_token)
        
        # --- 日志目录配置组 ---
        log_group = QGroupBox("日志目录配置")
        log_form = QFormLayout()
        log_group.setLayout(log_form)
        
        self.log_dir_live = QLineEdit(config.get("LOG_DIR_BASE_LIVE", ""))
        self.log_dir_postgame = QLineEdit(config.get("LOG_DIR_BASE_POSTGAME", ""))
        
        # 添加浏览按钮
        log_dir_live_layout = QHBoxLayout()
        log_dir_live_layout.addWidget(self.log_dir_live)
        browse_live_btn = QPushButton("浏览...")
        browse_live_btn.clicked.connect(lambda: browse_directory(self, self.log_dir_live))
        log_dir_live_layout.addWidget(browse_live_btn)
        
        # 添加打开文件夹按钮
        open_live_dir_btn = QPushButton("打开文件夹")
        open_live_dir_btn.setIcon(self.style().standardIcon(self.style().SP_DirOpenIcon))
        open_live_dir_btn.clicked.connect(lambda: self.open_directory(self.log_dir_live.text()))
        open_live_dir_btn.setToolTip("在文件资源管理器中打开此文件夹")
        log_dir_live_layout.addWidget(open_live_dir_btn)
        
        log_dir_postgame_layout = QHBoxLayout()
        log_dir_postgame_layout.addWidget(self.log_dir_postgame)
        browse_postgame_btn = QPushButton("浏览...")
        browse_postgame_btn.clicked.connect(lambda: browse_directory(self, self.log_dir_postgame))
        log_dir_postgame_layout.addWidget(browse_postgame_btn)
        
        # 添加打开文件夹按钮
        open_postgame_dir_btn = QPushButton("打开文件夹")
        open_postgame_dir_btn.setIcon(self.style().standardIcon(self.style().SP_DirOpenIcon))
        open_postgame_dir_btn.clicked.connect(lambda: self.open_directory(self.log_dir_postgame.text()))
        open_postgame_dir_btn.setToolTip("在文件资源管理器中打开此文件夹")
        log_dir_postgame_layout.addWidget(open_postgame_dir_btn)
        
        log_form.addRow("实时日志目录:", log_dir_live_layout)
        log_form.addRow("赛后日志目录:", log_dir_postgame_layout)
        
        # --- 轮询配置组 ---
        poll_group = QGroupBox("数据采集配置")
        poll_form = QFormLayout()
        poll_group.setLayout(poll_form)
        
        self.live_data_collect_interval = QSpinBox()
        self.live_data_collect_interval.setRange(1, 3600)  # 1秒到1小时
        self.live_data_collect_interval.setValue(config.get("LIVE_DATA_COLLECT_INTERVAL", 300))
        self.live_data_collect_interval.setSuffix(" 秒")
        
        self.max_eog_wait_time = QSpinBox()
        self.max_eog_wait_time.setRange(30, 600)
        self.max_eog_wait_time.setValue(config.get("MAX_EOG_WAIT_TIME", 120))
        self.max_eog_wait_time.setSuffix(" 秒")
        
        poll_form.addRow("实时数据采集间隔:", self.live_data_collect_interval)
        poll_form.addRow("赛后数据等待时间:", self.max_eog_wait_time)
        
        # --- 应用日志配置组 ---
        log_config_group = QGroupBox("应用日志配置")
        log_config_form = QFormLayout()
        log_config_group.setLayout(log_config_form)
        
        # 应用日志目录
        self.app_log_dir = QLineEdit(config.get("APP_LOG_DIR", ""))
        app_log_dir_layout = QHBoxLayout()
        app_log_dir_layout.addWidget(self.app_log_dir)
        
        # 浏览按钮
        browse_app_log_btn = QPushButton("浏览...")
        browse_app_log_btn.clicked.connect(lambda: browse_directory(self, self.app_log_dir))
        app_log_dir_layout.addWidget(browse_app_log_btn)
        
        # 添加打开文件夹按钮
        open_app_log_dir_btn = QPushButton("打开文件夹")
        open_app_log_dir_btn.setIcon(self.style().standardIcon(self.style().SP_DirOpenIcon))
        open_app_log_dir_btn.clicked.connect(lambda: self.open_directory(self.app_log_dir.text()))
        open_app_log_dir_btn.setToolTip("在文件资源管理器中打开此文件夹")
        app_log_dir_layout.addWidget(open_app_log_dir_btn)
        
        log_config_form.addRow("日志文件目录:", app_log_dir_layout)
        
        # 添加查看当前日志文件按钮
        view_current_log_btn = QPushButton("查看当前日志")
        view_current_log_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogContentsView))
        view_current_log_btn.clicked.connect(self.view_current_log_file)
        view_current_log_btn.setToolTip("查看当前应用程序的日志文件内容")
        
        # 添加查看历史日志按钮
        view_history_log_btn = QPushButton("查看历史日志")
        view_history_log_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogListView))
        view_history_log_btn.clicked.connect(self.view_history_logs)
        view_history_log_btn.setToolTip("查看历史日志文件列表")
        
        # 添加清空日志按钮
        clear_logs_btn = QPushButton("清空所有日志")
        clear_logs_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        clear_logs_btn.clicked.connect(self.clear_log_files)
        clear_logs_btn.setToolTip("删除所有应用程序日志文件")
        clear_logs_btn.setStyleSheet("QPushButton { color: red; }")
        
        # 创建按钮布局
        log_buttons_layout = QHBoxLayout()
        log_buttons_layout.addWidget(view_current_log_btn)
        log_buttons_layout.addWidget(view_history_log_btn)
        log_buttons_layout.addWidget(clear_logs_btn)
        
        log_config_form.addRow("", log_buttons_layout)
        
        # 添加日志空间使用信息
        self.log_space_info_label = QLabel("加载中...")
        self.log_space_info_label.setStyleSheet("QLabel { font-size: 9pt; }")
        log_config_form.addRow("", self.log_space_info_label)
        
        # 添加更新日志空间信息按钮
        refresh_space_btn = QPushButton("刷新日志空间使用信息")
        refresh_space_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        refresh_space_btn.clicked.connect(self.update_log_space_info)
        refresh_space_btn.setToolTip("刷新日志空间使用信息")
        log_config_form.addRow("", refresh_space_btn)
        
        # 初始化日志空间信息
        self.update_log_space_info()

        # --- 应用程序设置组 ---
        setting_group = QGroupBox("应用程序设置")
        app_form = QFormLayout()
        setting_group.setLayout(app_form)
        
        self.config_dir = QLineEdit(config.get("CONFIG_DIR", ""))
        
        # 添加浏览按钮
        config_dir_layout = QHBoxLayout()
        config_dir_layout.addWidget(self.config_dir)
        browse_config_btn = QPushButton("浏览...")
        browse_config_btn.clicked.connect(lambda: browse_directory(self, self.config_dir))
        config_dir_layout.addWidget(browse_config_btn)
        
        # 添加打开文件夹按钮
        open_config_dir_btn = QPushButton("打开文件夹")
        open_config_dir_btn.setIcon(self.style().standardIcon(self.style().SP_DirOpenIcon))
        open_config_dir_btn.clicked.connect(lambda: self.open_directory(self.config_dir.text()))
        open_config_dir_btn.setToolTip("在文件资源管理器中打开此文件夹")
        config_dir_layout.addWidget(open_config_dir_btn)
        
        app_form.addRow("配置文件目录:", config_dir_layout)
        
        # 配置文件说明
        config_note = QLabel("注意: 修改配置文件目录后，需要重启应用程序才能生效。新的配置文件将在重启后创建。")
        config_note.setWordWrap(True)
        config_note.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        app_form.addRow("", config_note)
        
        # 添加到主布局
        layout.addWidget(lcu_group)
        layout.addWidget(log_group)
        layout.addWidget(poll_group)
        layout.addWidget(log_config_group)
        layout.addWidget(setting_group)

        # 添加配置导入/导出按钮
        import_export_layout = QHBoxLayout()
        
        # 导入配置按钮
        import_btn = QPushButton("导入配置")
        import_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogStart))
        import_btn.setToolTip("从外部JSON文件导入配置")
        import_btn.clicked.connect(self.import_config)
        
        # 导出配置按钮
        export_btn = QPushButton("导出配置")
        export_btn.setIcon(self.style().standardIcon(self.style().SP_DialogSaveButton))
        export_btn.setToolTip("将当前配置导出到JSON文件")
        export_btn.clicked.connect(self.export_config)
        
        import_export_layout.addWidget(import_btn)
        import_export_layout.addWidget(export_btn)
        layout.addLayout(import_export_layout)
        
        # 添加保存和重置按钮
        save_layout = QHBoxLayout()
        
        # 重置按钮（重置表单值为默认值，但不删除配置文件）
        reset_btn = QPushButton("重置表单")
        reset_btn.setToolTip("重置为默认值，但不保存更改")
        reset_btn.clicked.connect(self.reset_settings)
        
        # 保存按钮
        save_btn = QPushButton("保存配置")
        save_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        save_btn.clicked.connect(self.save_settings)
        
        # 删除配置文件按钮
        delete_config_btn = QPushButton("删除配置文件")
        delete_config_btn.setStyleSheet("QPushButton { color: red; }")
        delete_config_btn.setToolTip("删除用户配置文件，完全重置为系统默认值")
        delete_config_btn.clicked.connect(self.delete_user_config)
        
        # 添加到布局
        save_layout.addWidget(delete_config_btn)
        save_layout.addWidget(reset_btn)
        save_layout.addWidget(save_btn)
        
        layout.addLayout(save_layout)
        
        # 添加配置文件路径信息
        config_info_layout = QHBoxLayout()
        self.config_path_label = QLabel(f"当前配置文件路径: {self.config_manager.config_file}")
        self.config_path_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        config_info_layout.addWidget(self.config_path_label)
        layout.addLayout(config_info_layout)
        
        layout.addStretch(1)  # 添加弹性空间
        
        # 初始化日志空间信息
        self.update_log_space_info()
    
    def save_settings(self):
        """保存设置到配置文件"""
        # 收集当前设置
        new_config = {
            "UPLOAD_API_URL": self.upload_api_url.text(),
            "LCU_EOG_ENDPOINT": self.lcu_eog_endpoint.text(),
            "LCU_PORT": self.lcu_port.text(),
            "LCU_TOKEN": self.lcu_token.text(),
            "LOG_DIR_BASE_LIVE": self.log_dir_live.text(),
            "LOG_DIR_BASE_POSTGAME": self.log_dir_postgame.text(),
            "LIVE_DATA_COLLECT_INTERVAL": self.live_data_collect_interval.value(),
            "MAX_EOG_WAIT_TIME": self.max_eog_wait_time.value(),
            "APP_LOG_DIR": self.app_log_dir.text(),
        }
        
        # 检查配置文件目录是否发生变化
        config_dir = self.config_dir.text().strip()
        if config_dir:
            # 构建新的配置文件路径
            config_file = os.path.join(config_dir, "config.json")
            
            # 检查是否与当前配置不同
            if config_dir != self.config_manager.current_config.get("CONFIG_DIR", ""):
                # 添加提示对话框，告知用户需要重启应用
                restart_needed = self.show_question(
                    "配置路径已更改",
                    "您修改了配置文件目录，新的配置将在应用程序重启后生效。\n\n"
                    f"新的配置文件将保存在：{config_file}\n\n"
                    "是否继续保存？"
                )
                
                if not restart_needed:
                    return
                
                # 添加到配置
                new_config["CONFIG_DIR"] = config_dir
                new_config["CONFIG_FILE"] = config_file
        
        try:
            # 保存配置
            self.config_manager.save_config(new_config)
            
            # 显示成功消息
            self.show_message("保存成功", "配置已成功保存！\n\n"
                           "- LCU API和轮询设置将在下次启动监控时生效\n"
                           "- 日志目录设置已立即生效，目录已创建\n"
                           "- 其他设置可能需要重启应用后生效")
            
            # 创建日志目录（如果不存在）
            create_directory_if_not_exists(new_config["LOG_DIR_BASE_LIVE"])
            create_directory_if_not_exists(new_config["LOG_DIR_BASE_POSTGAME"])
            
            # 创建应用日志目录（如果不存在）
            if "APP_LOG_DIR" in new_config and new_config["APP_LOG_DIR"]:
                create_directory_if_not_exists(new_config["APP_LOG_DIR"])
            
            # 刷新游戏数据管理标签页的游戏列表
            if self.main_window and hasattr(self.main_window, 'logs_tab'):
                self.main_window.logs_tab.refresh_game_list()
                
            # 记录配置修改的日志
            self.log_info("用户配置已更新")
            
        except Exception as e:
            # 显示错误消息
            self.show_error("保存失败", f"保存配置时出错:\n{str(e)}")
    
    def reset_settings(self):
        """重置设置为默认值（从config.py中读取的原始值）"""
        if self.show_question("确认重置", "确定要重置所有设置到默认值吗？"):
            # 重新加载原始配置
            original_config = self.config_manager.original_config
            
            # 更新界面
            self.upload_api_url.setText(original_config.get("UPLOAD_API_URL", ""))
            self.lcu_eog_endpoint.setText(original_config.get("LCU_EOG_ENDPOINT", ""))
            self.lcu_port.setText(original_config.get("LCU_PORT", ""))
            self.lcu_token.setText(original_config.get("LCU_TOKEN", ""))
            self.log_dir_live.setText(original_config.get("LOG_DIR_BASE_LIVE", ""))
            self.log_dir_postgame.setText(original_config.get("LOG_DIR_BASE_POSTGAME", ""))
            self.live_data_collect_interval.setValue(original_config.get("LIVE_DATA_COLLECT_INTERVAL", 300))
            self.max_eog_wait_time.setValue(original_config.get("MAX_EOG_WAIT_TIME", 120))
            self.config_dir.setText(original_config.get("CONFIG_DIR", ""))
            
            # 更新应用日志配置
            if hasattr(self, 'app_log_dir'):
                self.app_log_dir.setText(original_config.get("APP_LOG_DIR", ""))
            
    def delete_user_config(self):
        """删除用户配置文件，完全重置为默认配置"""
        if self.show_question("确认删除", "确定要删除用户配置文件，并重置为系统默认配置吗？\n\n这将删除您所有的自定义设置。"):
            try:
                # 删除配置文件
                if os.path.exists(self.config_manager.config_file):
                    os.remove(self.config_manager.config_file)
                
                # 重新加载配置
                self.config_manager.load_config()
                
                # 更新界面
                self.reset_settings()
                
                # 显示成功消息
                self.show_message("重置成功", "用户配置文件已删除，所有设置已重置为系统默认值。")
            except Exception as e:
                # 显示错误消息
                self.show_error("删除失败", f"删除配置文件时出错:\n{str(e)}")
    
    def export_config(self):
        """导出配置到JSON文件"""
        # 导出当前配置（包括表单中的修改，但不保存）
        current_settings = self.collect_current_settings()
        
        # 临时更新配置管理器的当前配置
        temp_config = self.config_manager.current_config.copy()
        self.config_manager.current_config.update(current_settings)
        
        # 导出配置
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"lcu_agent_config_{timestamp}.json"
        export_success = export_config_file(self, self.config_manager, default_name)
        
        # 恢复配置管理器的当前配置
        self.config_manager.current_config = temp_config
        
    def import_config(self):
        """从JSON文件导入配置"""
        # 导入配置
        imported_config = import_config_file(self, self.config_manager)
        
        if imported_config:
            # 确认是否应用导入的配置
            confirm = self.show_question(
                "确认导入", 
                "是否应用导入的配置？\n\n"
                "这将更新界面上的所有设置，但不会立即保存。\n"
                "您需要检查设置并手动点击'保存配置'按钮保存更改。"
            )
            
            if confirm:
                # 更新界面上的设置
                if "UPLOAD_API_URL" in imported_config:
                    self.upload_api_url.setText(imported_config.get("UPLOAD_API_URL", ""))
                if "LCU_EOG_ENDPOINT" in imported_config:
                    self.lcu_eog_endpoint.setText(imported_config.get("LCU_EOG_ENDPOINT", ""))
                if "LCU_PORT" in imported_config:
                    self.lcu_port.setText(imported_config.get("LCU_PORT", ""))
                if "LCU_TOKEN" in imported_config:
                    self.lcu_token.setText(imported_config.get("LCU_TOKEN", ""))
                if "LOG_DIR_BASE_LIVE" in imported_config:
                    self.log_dir_live.setText(imported_config.get("LOG_DIR_BASE_LIVE", ""))
                if "LOG_DIR_BASE_POSTGAME" in imported_config:
                    self.log_dir_postgame.setText(imported_config.get("LOG_DIR_BASE_POSTGAME", ""))
                if "LIVE_DATA_COLLECT_INTERVAL" in imported_config:
                    self.live_data_collect_interval.setValue(imported_config.get("LIVE_DATA_COLLECT_INTERVAL", 300))
                if "MAX_EOG_WAIT_TIME" in imported_config:
                    self.max_eog_wait_time.setValue(imported_config.get("MAX_EOG_WAIT_TIME", 120))
                if "CONFIG_DIR" in imported_config:
                    self.config_dir.setText(imported_config.get("CONFIG_DIR", ""))
                if "APP_LOG_DIR" in imported_config and hasattr(self, 'app_log_dir'):
                    self.app_log_dir.setText(imported_config.get("APP_LOG_DIR", ""))
                
                self.show_message("导入成功", "配置已成功导入！\n\n请检查设置并点击'保存配置'按钮保存更改。")
                self.log_info("成功导入配置")
            
    def collect_current_settings(self):
        """收集当前界面上的所有设置"""
        return {
            "UPLOAD_API_URL": self.upload_api_url.text(),
            "LCU_EOG_ENDPOINT": self.lcu_eog_endpoint.text(),
            "LCU_PORT": self.lcu_port.text(),
            "LCU_TOKEN": self.lcu_token.text(),
            "LOG_DIR_BASE_LIVE": self.log_dir_live.text(),
            "LOG_DIR_BASE_POSTGAME": self.log_dir_postgame.text(),
            "LIVE_DATA_COLLECT_INTERVAL": self.live_data_collect_interval.value(),
            "MAX_EOG_WAIT_TIME": self.max_eog_wait_time.value(),
            "CONFIG_DIR": self.config_dir.text().strip() if self.config_dir.text().strip() else None,
            "APP_LOG_DIR": self.app_log_dir.text() if hasattr(self, 'app_log_dir') else "",
        }
            
    def view_current_log_file(self):
        """查看当前日志文件内容"""
        try:
            # 使用单例日志管理器
            from ..utils.log_manager import get_logger
            log_manager = get_logger()
            
            # 获取日志文件路径
            log_file = log_manager.get_log_filepath()
            
            # 检查日志文件是否存在
            if not os.path.exists(log_file):
                self.show_error("错误", f"日志文件不存在: {log_file}")
                return
                
            # 打开日志文件
            if os.name == 'nt':  # Windows
                os.startfile(log_file)
            elif os.name == 'posix':  # macOS 和 Linux
                try:
                    subprocess.Popen(['open', log_file])  # macOS
                except:
                    subprocess.Popen(['xdg-open', log_file])  # Linux
            
            self.log_info(f"打开日志文件: {log_file}")
        except Exception as e:
            self.show_error("错误", f"打开日志文件时出错: {str(e)}")
            self.log_error(f"打开日志文件时出错: {str(e)}")
            
    def view_history_logs(self):
        """查看历史日志文件列表"""
        try:
            # 获取日志目录
            log_dir = self.app_log_dir.text() if self.app_log_dir.text() else self.config_manager.current_config.get("APP_LOG_DIR", "")
            
            # 如果日志目录为空，则使用默认日志目录
            if not log_dir:
                documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                log_dir = os.path.join(documents_dir, "LoL-Data-Collector", "app_logs")
            
            # 确保日志目录存在
            if not os.path.exists(log_dir):
                self.show_message("历史日志", "日志目录不存在。")
                return
                
            # 获取所有日志文件
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            
            if not log_files:
                self.show_message("历史日志", "没有找到日志文件。")
                return
                
            # 打开日志目录
            self.open_directory(log_dir)
            
        except Exception as e:
            self.show_error("错误", f"查看历史日志文件时出错: {str(e)}")
            self.log_error(f"查看历史日志文件时出错: {str(e)}")
    
    def clear_log_files(self):
        """清空日志文件"""
        try:
            confirm = self.show_question(
                "确认清空", 
                "确定要清空所有日志文件吗？\n\n"
                "这将删除应用程序的所有日志文件，此操作无法撤销。"
            )
            
            if not confirm:
                return
                
            # 获取日志目录
            log_dir = self.app_log_dir.text() if self.app_log_dir.text() else self.config_manager.current_config.get("APP_LOG_DIR", "")
            
            # 如果日志目录为空，则使用默认日志目录
            if not log_dir:
                documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                log_dir = os.path.join(documents_dir, "LoL-Data-Collector", "app_logs")
            
            # 确保日志目录存在
            if not os.path.exists(log_dir):
                self.show_message("清空完成", "日志目录不存在，无需清空。")
                return
                
            # 获取所有日志文件
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            
            if not log_files:
                self.show_message("清空完成", "没有找到日志文件。")
                return
            
            # 使用单例日志管理器，先关闭所有处理器
            from ..utils.log_manager import get_logger
            log_manager = get_logger()
            log_manager.close_handlers()
                
            # 短暂等待文件释放
            import time
            time.sleep(0.1)
                
            # 删除所有日志文件
            failed_files = []
            for log_file in log_files:
                file_path = os.path.join(log_dir, log_file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    failed_files.append(file_path)
                    self.log_error(f"删除日志文件失败: {file_path}, 错误: {str(e)}")
            
            # 重新初始化日志文件
            log_manager.init_handlers()
            # 记录清空日志的操作
            log_manager.info("用户已清空所有日志文件")
                
            # 显示结果消息
            if failed_files:
                self.show_message("清空部分完成", 
                               f"已删除 {len(log_files) - len(failed_files)} 个日志文件。\n"
                               f"{len(failed_files)} 个文件无法删除，可能仍在使用中。")
            else:
                self.show_message("清空完成", f"已删除 {len(log_files)} 个日志文件。")
            
            self.log_info(f"已清空日志文件，共 {len(log_files) - len(failed_files)} 个")
            
            # 更新日志空间使用信息
            self.update_log_space_info()
            
        except Exception as e:
            self.show_error("错误", f"清空日志文件时出错: {str(e)}")
            self.log_error(f"清空日志文件时出错: {str(e)}")
    
    def get_directory_size(self, path):
        """获取目录总大小（单位：字节）"""
        total_size = 0
        if os.path.exists(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        return total_size
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
    def open_directory(self, directory_path):
        """在文件资源管理器中打开目录"""
        try:
            if not directory_path:
                # 如果目录路径为空，则尝试获取默认路径
                if hasattr(self, 'app_log_dir'):
                    directory_path = self.config_manager.current_config.get("APP_LOG_DIR", "")
                
                # 如果还是空，则使用默认日志目录
                if not directory_path:
                    documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                    directory_path = os.path.join(documents_dir, "LoL-Data-Collector", "app_logs")
            
            # 确保目录存在
            create_directory_if_not_exists(directory_path)
            
            # 打开目录
            if os.name == 'nt':  # Windows
                os.startfile(directory_path)
            elif os.name == 'posix':  # macOS 和 Linux
                try:
                    subprocess.Popen(['open', directory_path])  # macOS
                except:
                    subprocess.Popen(['xdg-open', directory_path])  # Linux
                    
            self.log_info(f"已打开目录: {directory_path}")
        except Exception as e:
            self.show_error("错误", f"打开目录时出错: {str(e)}")
            self.log_error(f"打开目录时出错: {str(e)}")
    
    def update_log_space_info(self):
        """更新日志空间使用信息"""
        try:
            # 获取日志目录
            log_dir = self.app_log_dir.text() if self.app_log_dir.text() else self.config_manager.current_config.get("APP_LOG_DIR", "")
            
            # 如果日志目录为空，则使用默认日志目录
            if not log_dir:
                documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
                log_dir = os.path.join(documents_dir, "LoL-Data-Collector", "app_logs")
            
            # 如果日志目录不存在，显示为0
            if not os.path.exists(log_dir):
                if hasattr(self, 'log_space_info_label'):
                    self.log_space_info_label.setText("日志空间使用: 0 B (0 个文件)")
                return
                
            # 获取日志文件数量和总大小
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            total_size = self.get_directory_size(log_dir)
            
            # 更新标签文本
            if hasattr(self, 'log_space_info_label'):
                self.log_space_info_label.setText(f"日志空间使用: {self.format_size(total_size)} ({len(log_files)} 个文件)")
                
                # 根据大小设置不同颜色
                if total_size > 10 * 1024 * 1024:  # 大于10MB显示红色
                    self.log_space_info_label.setStyleSheet("QLabel { color: red; }")
                elif total_size > 5 * 1024 * 1024:  # 大于5MB显示橙色
                    self.log_space_info_label.setStyleSheet("QLabel { color: orange; }")
                else:
                    self.log_space_info_label.setStyleSheet("QLabel { color: green; }")
            
        except Exception as e:
            self.log_error(f"更新日志空间使用信息时出错: {str(e)}")