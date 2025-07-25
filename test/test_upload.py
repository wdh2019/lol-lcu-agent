"""
测试脚本 - 上传游戏日志
这个脚本用于上传游戏日志，便于调试
"""
import sys
import os
# 添加项目根目录到路径，以便能够导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.log_uploader import upload_game_logs_manually

if __name__ == "__main__":
    print("启动日志上传模式...")
    
    # 检查命令行参数，可以指定游戏文件夹
    game_folder = None
    if len(sys.argv) > 1:
        game_folder = sys.argv[1]
        print(f"将上传指定游戏文件夹: {game_folder}")
    
    # 调用上传函数
    upload_game_logs_manually(game_folder)
