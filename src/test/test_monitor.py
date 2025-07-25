"""
测试脚本 - 直接运行游戏监控
这个脚本用于直接启动游戏监控功能，便于调试
"""
import sys
import os
# 添加项目根目录到路径，以便能够导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.game_monitor import main_loop

if __name__ == "__main__":
    print("启动命令行模式游戏监控...")
    print("按Ctrl+C停止监控")
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n用户中断，停止监控")
