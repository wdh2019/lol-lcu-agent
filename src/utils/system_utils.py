import subprocess
from .log_manager import get_logger

def list_running_processes():
    """
    列出当前系统中正在运行的进程
    进程信息将记录到日志文件中
    """
    # 使用单例日志管理器
    log_manager = get_logger()
    
    try:
        log_msg = "\n正在获取系统中运行的进程列表..."
        print(log_msg)
        log_manager.info(log_msg)
            
        command = "wmic process get name,processid"
        output = subprocess.check_output(command, shell=True, text=True)
        
        # 处理输出，按行分割并移除空行
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        if lines:
            # 添加表头到日志
            header_line = f"{'进程名称':<40} {'进程ID':<10}"
            divider_line = "-" * 50
            
            # 打印表头
            print(f"\n{header_line}")
            print(divider_line)
            
            # 记录进程列表开始到日志
            log_manager.info("系统进程列表:")
            log_manager.info(header_line)
            log_manager.info(divider_line)
            
            # 处理并显示每一行
            for line in lines[1:]:  # 跳过表头行
                # 分割进程名和ID，确保有足够的部分
                parts = line.split()
                if parts:
                    # 最后一个部分是PID，其余的是进程名称
                    pid = parts[-1]
                    name = ' '.join(parts[:-1])
                    formatted_line = f"{name:<40} {pid:<10}"
                    print(formatted_line)
                    
                    # 记录每个进程到日志
                    log_manager.debug(formatted_line)
                    
                    # 特别记录英雄联盟客户端进程
                    if "LeagueClient" in name or "League of Legends" in name:
                        log_manager.info(f"找到游戏相关进程: {name} (PID: {pid})")
            
            total_processes = len(lines) - 1
            summary_line = f"总共找到 {total_processes} 个进程"
            print(f"\n{summary_line}")
            log_manager.info(summary_line)
            
        else:
            log_msg = "未找到任何进程信息"
            print(log_msg)
            log_manager.warning(log_msg)
            
    except subprocess.SubprocessError as e:
        error_msg = f"获取进程列表时出错 (SubprocessError): {e}"
        print(error_msg)
        log_manager.error(error_msg)
    except Exception as e:
        error_msg = f"获取进程列表时出错: {e}"
        print(error_msg)
        log_manager.error(error_msg)
