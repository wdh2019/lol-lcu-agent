"""
日志管理器使用示例
演示如何在项目中使用单例模式的日志管理器
"""

# 方式1: 直接导入并使用默认实例
from .log_manager import logger

def example_function_1():
    logger.info("这是来自示例函数1的日志")
    logger.debug("调试信息")
    logger.warning("警告信息")


# 方式2: 使用便捷函数获取实例
from .log_manager import get_logger

def example_function_2():
    log_manager = get_logger()
    log_manager.info("这是来自示例函数2的日志")
    try:
        # 模拟一个错误
        raise ValueError("这是一个测试错误")
    except Exception as e:
        log_manager.error(f"捕获到错误: {str(e)}")


# 方式3: 直接使用LogManager类方法
from .log_manager import LogManager

def example_function_3():
    log_manager = LogManager.get_instance()
    log_manager.info("这是来自示例函数3的日志")


# 方式4: 在模块级别初始化（推荐用于需要自定义配置的情况）
def initialize_logger_with_custom_config():
    """初始化日志管理器，只在应用启动时调用一次"""
    import logging
    
    # 第一次调用会进行初始化，后续调用会返回同一个实例
    log_manager = LogManager(
        log_dir="./custom_logs",  # 自定义日志目录
        log_level=logging.DEBUG,  # 设置为DEBUG级别
        console_output=True       # 启用控制台输出
    )
    
    # 设置全局异常处理
    log_manager.set_exception_hook()
    
    # 清理旧日志（保留7天）
    log_manager.cleanup_old_logs(max_age_days=7)
    
    return log_manager


if __name__ == "__main__":
    # 应用启动时初始化日志管理器
    log_manager = initialize_logger_with_custom_config()
    
    # 在不同函数中使用日志，都会使用同一个实例
    example_function_1()
    example_function_2()
    example_function_3()
    
    # 验证单例模式：所有方式获取的都是同一个实例
    logger1 = logger
    logger2 = get_logger()
    logger3 = LogManager.get_instance()
    logger4 = LogManager()  # 即使再次调用构造函数，也会返回同一个实例
    
    print(f"logger1 id: {id(logger1)}")
    print(f"logger2 id: {id(logger2)}")
    print(f"logger3 id: {id(logger3)}")
    print(f"logger4 id: {id(logger4)}")
    print(f"所有实例都相同: {logger1 is logger2 is logger3 is logger4}")
