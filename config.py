"""
全局配置项
"""

# --- Live Client Data API 配置 ---
# 游戏内实时数据API
LIVE_DATA_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"
# LCU API (客户端API) 的赛后数据端点
LCU_EOG_ENDPOINT = "/lol-end-of-game/v1/eog-stats-block"
# LCU 连接凭证 (根据您的电脑环境提取)
LCU_PORT = "54694"
LCU_TOKEN = "u6fbXvHqfOHWk"

# --- 日志目录配置 ---
# 本地日志文件夹
LOG_DIR_BASE_LIVE = "game_logs_live"
LOG_DIR_BASE_POSTGAME = "game_logs_postgame"

# --- 轮询配置 ---
# 轮询间隔（秒）
POLL_INTERVAL = 5  # 减小轮询间隔，提高响应速度
# 赛后数据最大等待时间（秒）
MAX_EOG_WAIT_TIME = 120  # 等待2分钟

# --- 日志上传配置 ---
UPLOAD_LOGS = True  # 是否自动上传日志
LOG_SERVER_URL = "https://example.com/api/upload-logs"  # 日志上传服务器URL
