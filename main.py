"""
英雄联盟游戏数据采集工具 - 主程序
"""
import sys
from utils.game_monitor import main_loop
from utils.log_uploader import upload_game_logs_manually


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "upload":
            # 仅上传模式
            game_folder = sys.argv[2] if len(sys.argv) > 2 else None
            upload_game_logs_manually(game_folder)
        elif sys.argv[1].lower() == "gui":
            # 图形界面模式
            try:
                from ui.main_window import main as run_ui
                run_ui()
            except ImportError as e:
                print(f"启动图形界面失败: {e}")
                print("请确保已安装PyQt5: pip install PyQt5")
        elif sys.argv[1].lower() == "help" or sys.argv[1].lower() == "--help" or sys.argv[1].lower() == "-h":
            print("使用方法:")
            print("  python main.py               # 正常模式，监控游戏并采集数据")
            print("  python main.py upload        # 上传模式，将显示所有可用游戏文件夹供您选择上传")
            print("  python main.py upload [游戏文件夹名]  # 直接上传指定游戏的日志")
            print("  python main.py gui           # 启动图形界面")
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 'python main.py help' 查看帮助")
    else:
        # 正常模式
        main_loop()
