"""
全局配置项
"""

# --- Live Client Data API 配置 ---
LIVE_DATA_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"
LCU_EOG_ENDPOINT = "/lol-end-of-game/v1/eog-stats-block"
LCU_PORT = "54694"
LCU_TOKEN = "u6fbXvHqfOHWk"

# --- 日志目录配置 ---
LOG_DIR_BASE_LIVE = "D:/test/logs_live"
LOG_DIR_BASE_POSTGAME = "D:/test/logs_postgame"

# --- 轮询配置 ---
POLL_INTERVAL = 10  # 减小轮询间隔，提高响应速度
MAX_EOG_WAIT_TIME = 120  # 等待2分钟

# --- 日志上传配置 ---
UPLOAD_LOGS = True  # 是否自动上传日志
LOG_SERVER_URL = "http://example.com/upload"  # 日志上传服务器地址
