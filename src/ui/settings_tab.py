"""
设置标签页
"""
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QFormLayout, QGroupBox, QSpinBox,
                            QCheckBox)
from PyQt5.QtCore import Qt

from .base_tab import BaseTab
from .ui_utils import browse_directory, create_directory_if_not_exists

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
        
        self.live_data_url = QLineEdit(config.get("LIVE_DATA_URL", ""))
        self.lcu_eog_endpoint = QLineEdit(config.get("LCU_EOG_ENDPOINT", ""))
        self.lcu_port = QLineEdit(config.get("LCU_PORT", ""))
        self.lcu_token = QLineEdit(config.get("LCU_TOKEN", ""))
        
        lcu_form.addRow("游戏实时数据 URL:", self.live_data_url)
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
        
        log_dir_postgame_layout = QHBoxLayout()
        log_dir_postgame_layout.addWidget(self.log_dir_postgame)
        browse_postgame_btn = QPushButton("浏览...")
        browse_postgame_btn.clicked.connect(lambda: browse_directory(self, self.log_dir_postgame))
        log_dir_postgame_layout.addWidget(browse_postgame_btn)
        
        log_form.addRow("实时日志目录:", log_dir_live_layout)
        log_form.addRow("赛后日志目录:", log_dir_postgame_layout)
        
        # --- 轮询配置组 ---
        poll_group = QGroupBox("轮询配置")
        poll_form = QFormLayout()
        poll_group.setLayout(poll_form)
        
        self.poll_interval = QSpinBox()
        self.poll_interval.setRange(1, 60)
        self.poll_interval.setValue(config.get("POLL_INTERVAL", 5))
        self.poll_interval.setSuffix(" 秒")
        
        self.max_eog_wait_time = QSpinBox()
        self.max_eog_wait_time.setRange(30, 600)
        self.max_eog_wait_time.setValue(config.get("MAX_EOG_WAIT_TIME", 120))
        self.max_eog_wait_time.setSuffix(" 秒")
        
        poll_form.addRow("轮询间隔:", self.poll_interval)
        poll_form.addRow("赛后数据等待时间:", self.max_eog_wait_time)
        
        # --- 日志上传配置组 ---
        upload_group = QGroupBox("日志上传配置")
        upload_form = QFormLayout()
        upload_group.setLayout(upload_form)
        
        self.upload_logs = QCheckBox("自动上传日志")
        self.upload_logs.setChecked(config.get("UPLOAD_LOGS", True))
        
        self.log_server_url = QLineEdit(config.get("LOG_SERVER_URL", ""))
        
        upload_form.addRow("", self.upload_logs)
        upload_form.addRow("上传服务器 URL:", self.log_server_url)
        
        # 添加所有配置组到主布局
        layout.addWidget(lcu_group)
        layout.addWidget(log_group)
        layout.addWidget(poll_group)
        layout.addWidget(upload_group)
        
        # 添加保存按钮
        save_layout = QHBoxLayout()
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_settings)
        reset_btn = QPushButton("重置默认")
        reset_btn.clicked.connect(self.reset_settings)
        save_layout.addWidget(reset_btn)
        save_layout.addWidget(save_btn)
        
        layout.addLayout(save_layout)
        layout.addStretch(1)  # 添加弹性空间
    
    def save_settings(self):
        """保存设置到配置文件"""
        # 收集当前设置
        new_config = {
            "LIVE_DATA_URL": self.live_data_url.text(),
            "LCU_EOG_ENDPOINT": self.lcu_eog_endpoint.text(),
            "LCU_PORT": self.lcu_port.text(),
            "LCU_TOKEN": self.lcu_token.text(),
            "LOG_DIR_BASE_LIVE": self.log_dir_live.text(),
            "LOG_DIR_BASE_POSTGAME": self.log_dir_postgame.text(),
            "POLL_INTERVAL": self.poll_interval.value(),
            "MAX_EOG_WAIT_TIME": self.max_eog_wait_time.value(),
            "UPLOAD_LOGS": self.upload_logs.isChecked(),
            "LOG_SERVER_URL": self.log_server_url.text()
        }
        
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
            
            # 刷新日志管理标签页的游戏列表
            if self.main_window and hasattr(self.main_window, 'logs_tab'):
                self.main_window.logs_tab.refresh_game_list()
            
        except Exception as e:
            # 显示错误消息
            self.show_error("保存失败", f"保存配置时出错:\n{str(e)}")
    
    def reset_settings(self):
        """重置设置为默认值"""
        if self.show_confirm("确认重置", "确定要重置所有设置到默认值吗？"):
            # 重新加载原始配置
            original_config = self.config_manager.original_config
            
            # 更新界面
            self.live_data_url.setText(original_config.get("LIVE_DATA_URL", ""))
            self.lcu_eog_endpoint.setText(original_config.get("LCU_EOG_ENDPOINT", ""))
            self.lcu_port.setText(original_config.get("LCU_PORT", ""))
            self.lcu_token.setText(original_config.get("LCU_TOKEN", ""))
            self.log_dir_live.setText(original_config.get("LOG_DIR_BASE_LIVE", ""))
            self.log_dir_postgame.setText(original_config.get("LOG_DIR_BASE_POSTGAME", ""))
            self.poll_interval.setValue(original_config.get("POLL_INTERVAL", 5))
            self.max_eog_wait_time.setValue(original_config.get("MAX_EOG_WAIT_TIME", 120))
            self.upload_logs.setChecked(original_config.get("UPLOAD_LOGS", True))
            self.log_server_url.setText(original_config.get("LOG_SERVER_URL", ""))
