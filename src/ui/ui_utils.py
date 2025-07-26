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

def export_files_to_zip(parent, files_to_zip, default_name=None):
    """
    将多个文件导出为一个zip压缩包
    
    参数:
        parent: 父窗口
        files_to_zip: 要打包的文件列表，每个元素是一个字典，包含 full_path 和 archive_name
        default_name: 默认保存的压缩包文件名
    """
    # 如果文件列表为空，直接返回
    if not files_to_zip:
        parent.show_warning("导出错误", "没有找到可导出的文件")
        return False
    
    # 设置默认保存的文件名
    if default_name is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"exported_files_{timestamp}.zip"
    
    # 让用户选择保存位置
    save_path, _ = QFileDialog.getSaveFileName(parent, "导出为ZIP", default_name, "ZIP文件 (*.zip)")
    
    if not save_path:
        return False  # 用户取消
    
    # 如果未指定.zip扩展名，添加它
    if not save_path.lower().endswith('.zip'):
        save_path += '.zip'
    
    try:
        # 创建ZIP文件
        with zipfile.ZipFile(save_path, 'w') as zipf:
            # 添加所有文件
            for file_info in files_to_zip:
                zipf.write(file_info['full_path'], file_info['archive_name'])
        
        parent.show_message("导出成功", f"已成功导出 {len(files_to_zip)} 个文件到:\n{save_path}")
        return True
    except Exception as e:
        parent.show_error("导出错误", f"创建ZIP文件时发生错误:\n{str(e)}")
        return False

def export_config_file(parent, config_manager, default_name=None):
    """
    导出配置文件
    
    参数:
        parent: 父窗口
        config_manager: 配置管理器
        default_name: 默认保存的文件名
    """
    if default_name is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"lcu_agent_config_{timestamp}.json"
    
    # 让用户选择保存位置
    save_path, _ = QFileDialog.getSaveFileName(parent, "导出配置文件", default_name, "JSON文件 (*.json)")
    
    if not save_path:
        return False  # 用户取消
    
    # 如果未指定.json扩展名，添加它
    if not save_path.lower().endswith('.json'):
        save_path += '.json'
    
    try:
        # 获取当前配置
        config_data = config_manager.current_config
        
        # 写入JSON文件
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        
        parent.show_message("导出成功", f"配置已成功导出到:\n{save_path}")
        return True
    except Exception as e:
        parent.show_error("导出错误", f"导出配置文件时发生错误:\n{str(e)}")
        return False

def import_config_file(parent, config_manager):
    """
    导入配置文件
    
    参数:
        parent: 父窗口
        config_manager: 配置管理器
    """
    # 让用户选择配置文件
    file_path, _ = QFileDialog.getOpenFileName(parent, "导入配置文件", "", "JSON文件 (*.json)")
    
    if not file_path:
        return None  # 用户取消
    
    try:
        # 读取配置文件
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 验证配置数据
        required_keys = ["LIVE_DATA_URL", "LCU_EOG_ENDPOINT", "LOG_DIR_BASE_LIVE", "LOG_DIR_BASE_POSTGAME"]
        missing_keys = [key for key in required_keys if key not in config_data]
        
        if missing_keys:
            parent.show_warning("导入错误", f"配置文件缺少必要的配置项:\n{', '.join(missing_keys)}\n\n可能不是有效的配置文件。")
            return None
        
        return config_data
    except json.JSONDecodeError:
        parent.show_warning("格式错误", "所选文件不是有效的JSON格式")
    except Exception as e:
        parent.show_error("导入错误", f"导入配置文件时发生错误:\n{str(e)}")
    
    return None
