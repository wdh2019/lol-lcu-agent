"""
英雄联盟游戏数据采集工具 - 主入口
"""
import sys
import os
import logging

# 初始化日志系统
def initialize_logging():
    """初始化日志系统"""
    try:
        from src.utils.log_manager import LogManager
        from src.config import APP_LOG_DIR, APP_LOG_LEVEL
        
        # 转换日志级别字符串为logging常量
        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = log_level_map.get(APP_LOG_LEVEL, logging.INFO)
        
        # 创建日志管理器实例（单例）
        log_manager = LogManager(log_dir=APP_LOG_DIR, log_level=log_level)
        
        # 设置全局异常钩子，捕获未处理的异常
        log_manager.set_exception_hook()
        
        # 记录应用程序启动信息
        log_manager.info(f"应用程序启动 - 版本: 1.0.0")
        log_manager.info(f"Python版本: {sys.version}")
        log_manager.info(f"工作目录: {os.getcwd()}")
        
        return True
    except Exception as e:
        print(f"初始化日志系统失败: {str(e)}")
        return False

def show_help():
    """显示帮助信息"""
    print("使用方法:")
    print("  python main.py               # 启动图形界面")
    print("  python main.py --help        # 显示此帮助信息")
    print("\n要使用其他功能（如命令行监控或上传），请使用test文件夹中的脚本")

if __name__ == "__main__":
    # 初始化日志系统
    log_initialized = initialize_logging()
    
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
            if log_initialized:
                from src.utils.log_manager import get_logger
                log_manager = get_logger()
                log_manager.info("正在启动图形界面...")
            print("正在启动图形界面...")
            
            from src.ui.main_window import main as run_ui
            run_ui()
        except ImportError as e:
            error_message = f"启动图形界面失败: {e}\n请确保已安装PyQt5: pip install PyQt5"
            print(error_message)
            if log_initialized:
                from src.utils.log_manager import get_logger
                get_logger().error(error_message)
        except Exception as e:
            error_message = f"启动过程中发生错误: {str(e)}"
            print(error_message)
            if log_initialized:
                from src.utils.log_manager import get_logger
                get_logger().error(error_message, exc_info=True)
