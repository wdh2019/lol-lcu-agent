"""
全局配置项
"""

# --- Live Client Data API 配置 ---
LIVE_DATA_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"
LCU_EOG_ENDPOINT = "/lol-end-of-game/v1/eog-stats-block"
LCU_PORT = "54694"
LCU_TOKEN = "u6fbXvHqfOHWk"

# --- 日志目录配置 ---
import os
# 使用用户文档目录下的 LoL-Data-Collector 文件夹作为默认路径
documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
LOG_DIR_BASE_LIVE = os.path.join(documents_dir, "LoL-Data-Collector", "logs_live")
LOG_DIR_BASE_POSTGAME = os.path.join(documents_dir, "LoL-Data-Collector", "logs_postgame")

# --- 轮询配置 ---
POLL_INTERVAL = 10  # 减小轮询间隔，提高响应速度
MAX_EOG_WAIT_TIME = 120  # 等待2分钟

# --- 日志上传配置 ---
UPLOAD_LOGS = True  # 是否自动上传日志
LOG_SERVER_URL = "http://example.com/upload"  # 日志上传服务器地址

# --- 应用程序配置 ---
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".lcu-agent")  # 配置文件目录
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")  # 配置文件路径

# --- 运行日志配置 ---
APP_LOG_DIR = os.path.join(documents_dir, "LoL-Data-Collector", "app_logs")  # 应用程序日志目录
APP_LOG_LEVEL = "INFO"  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
