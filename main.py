"""
英雄联盟游戏数据采集工具 - 主入口
"""
import sys

def show_help():
    """显示帮助信息"""
    print("使用方法:")
    print("  python main.py               # 启动图形界面")
    print("  python main.py --help        # 显示此帮助信息")
    print("\n要使用其他功能（如命令行监控或上传），请使用test文件夹中的脚本")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ["help", "--help", "-h"]:
            show_help()
        else:
            print(f"未知参数: {sys.argv[1]}")
            show_help()
    else:
        # 默认启动UI界面
        try:
            from src.ui.main_window import main as run_ui
            print("正在启动图形界面...")
            run_ui()
        except ImportError as e:
            print(f"启动图形界面失败: {e}")
            print("请确保已安装PyQt5: pip install PyQt5")
