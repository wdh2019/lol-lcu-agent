"""
UI共用工具函数
"""
import os
import json
import datetime
import zipfile
from PyQt5.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QTextEdit

def format_file_size(size_bytes):
    """
    将文件大小格式化为人类可读的形式
    
    参数:
        size_bytes: 文件大小(字节)
    
    返回:
        格式化后的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def browse_directory(parent, line_edit, title="选择目录"):
    """
    打开目录选择对话框
    
    参数:
        parent: 父窗口
        line_edit: 要填充目录路径的QLineEdit控件
        title: 对话框标题
    """
    directory = QFileDialog.getExistingDirectory(parent, title, line_edit.text())
    if directory:
        line_edit.setText(directory)
        return True
    return False

def create_directory_if_not_exists(directory_path):
    """
    如果目录不存在则创建
    
    参数:
        directory_path: 目录路径
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        return True
    return False

def view_json_content(parent, file_path):
    """
    查看JSON文件内容
    
    参数:
        parent: 父窗口
        file_path: JSON文件路径
    """
    try:
        # 读取JSON文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 格式化JSON显示
        json_text = json.dumps(json_data, indent=4, ensure_ascii=False)
        
        # 创建查看窗口
        dialog = QDialog(parent)
        dialog.setWindowTitle(f"查看文件内容 - {os.path.basename(file_path)}")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(json_text)
        layout.addWidget(text_edit)
        
        dialog.exec_()
        return True
        
    except json.JSONDecodeError:
        parent.show_warning("格式错误", "文件不是有效的JSON格式")
    except Exception as e:
        parent.show_error("查看错误", f"查看文件内容时发生异常:\n{str(e)}")
    
    return False

def export_file(parent, source_path, default_name=None):
    """
    导出文件到用户选择的位置
    
    参数:
        parent: 父窗口
        source_path: 源文件路径
        default_name: 默认保存的文件名，如果为None则使用源文件名
    """
    if not os.path.exists(source_path):
        parent.show_error("导出错误", "源文件不存在")
        return False
    
    default_name = default_name or os.path.basename(source_path)
    
    # 使用文件保存对话框
    save_path, _ = QFileDialog.getSaveFileName(
        parent, "导出文件", 
        default_name, 
        "JSON文件 (*.json);;所有文件 (*)"
    )
    
    if not save_path:  # 用户取消
        return False
    
    try:
        # 复制文件
        import shutil
        shutil.copy2(source_path, save_path)
        parent.show_message("导出成功", f"文件已成功导出到:\n{save_path}")
        parent.update_status(f"文件已导出至 {save_path}")
        return True
    except Exception as e:
        parent.show_error("导出错误", f"导出文件时发生异常:\n{str(e)}")
        parent.update_status(f"导出失败: {str(e)}")
        return False

def export_files_to_zip(parent, file_list, save_path=None, default_name="logs_export.zip", file_type_filter="ZIP文件 (*.zip);;所有文件 (*)"):
    """
    将多个文件导出为ZIP压缩包
    
    参数:
        parent: 父窗口，用于显示消息和状态
        file_list: 文件信息列表，每项为字典 {'full_path': 完整路径, 'archive_name': 在压缩包内的路径}
        save_path: 保存路径，如果为None则弹出对话框选择
        default_name: 默认文件名
        file_type_filter: 文件类型过滤器
    
    返回:
        成功返回True，失败返回False
    """
    if not file_list:
        parent.show_warning("导出错误", "没有可导出的文件")
        return False
    
    # 如果没有指定保存路径，则弹出选择对话框
    if save_path is None:
        save_path, _ = QFileDialog.getSaveFileName(
            parent, "导出为压缩包", 
            default_name, 
            file_type_filter
        )
        
        if not save_path:  # 用户取消
            return False
    
    # 确保文件路径以.zip结尾
    if not save_path.lower().endswith('.zip'):
        save_path += '.zip'
        
    try:
        # 创建ZIP文件
        parent.update_status(f"正在创建压缩包，共 {len(file_list)} 个文件...")
        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in file_list:
                # 检查文件是否存在
                if not os.path.exists(file_info['full_path']):
                    parent.update_status(f"跳过不存在的文件: {file_info['full_path']}")
                    continue
                    
                # 将文件写入压缩包
                zipf.write(file_info['full_path'], file_info['archive_name'])
        
        parent.show_message("导出成功", f"文件已成功导出为压缩包:\n{save_path}")
        parent.update_status(f"已导出压缩包: {os.path.basename(save_path)}")
        return True
    except Exception as e:
        parent.show_error("导出错误", f"创建压缩包时发生异常:\n{str(e)}")
        parent.update_status(f"导出压缩包失败: {str(e)}")
        return False
