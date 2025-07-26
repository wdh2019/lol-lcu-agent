import subprocess
import os
from datetime import datetime

def list_running_processes(log_manager=None, save_to_file=True):
    """
    列出当前系统中正在运行的进程
    
    参数:
        log_manager: 日志管理器，如果提供则记录日志
        save_to_file: 是否将进程列表保存到文件中
    """
    try:
        log_msg = "\n正在获取系统中运行的进程列表..."
        print(log_msg)
        if log_manager:
            log_manager.info(log_msg)
            
        command = "wmic process get name,processid"
        output = subprocess.check_output(command, shell=True, text=True)
        
        # 处理输出，按行分割并移除空行
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        if lines:
            # 创建要显示和保存的内容
            process_list_content = []
            
            # 添加表头
            header_line = f"{'进程名称':<40} {'进程ID':<10}"
            divider_line = "-" * 50
            process_list_content.append(header_line)
            process_list_content.append(divider_line)
            
            # 打印表头
            print(f"\n{header_line}")
            print(divider_line)
            if log_manager:
                log_manager.debug(f"进程列表:\n{header_line}\n{divider_line}")
            
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
                    process_list_content.append(formatted_line)
                    
                    # 特别记录英雄联盟客户端进程
                    if "LeagueClient" in name or "League of Legends" in name:
                        if log_manager:
                            log_manager.info(f"找到游戏相关进程: {name} (PID: {pid})")
            
            total_processes = len(lines) - 1
            summary_line = f"\n总共找到 {total_processes} 个进程"
            print(summary_line)
            process_list_content.append(summary_line)
            if log_manager:
                log_manager.info(summary_line)
            
            # 保存到文件
            if save_to_file:
                # 创建目录(如果不存在)
                logs_dir = "process_logs"
                if not os.path.exists(logs_dir):
                    os.makedirs(logs_dir)
                
                # 使用时间戳创建文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(logs_dir, f"processes_{timestamp}.txt")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(process_list_content))
                
                log_msg = f"\n进程列表已保存到: {file_path}"
                print(log_msg)
                if log_manager:
                    log_manager.info(log_msg)
        else:
            log_msg = "未找到任何进程信息"
            print(log_msg)
            if log_manager:
                log_manager.warning(log_msg)
            
    except subprocess.SubprocessError as e:
        error_msg = f"获取进程列表时出错 (SubprocessError): {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
    except Exception as e:
        error_msg = f"获取进程列表时出错: {e}"
        print(error_msg)
        if log_manager:
            log_manager.error(error_msg)
