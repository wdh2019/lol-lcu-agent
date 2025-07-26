"""
构建脚本，用于将项目打包成可执行文件
"""

import os
import sys
import shutil
import subprocess
import datetime

# 获取项目根目录
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def check_pyinstaller():
    """检查是否已安装PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("PyInstaller安装完成")

def build_executable(one_file=True, console=False):
    """构建可执行文件"""
    # 切换到项目根目录
    os.chdir(ROOT_DIR)
    
    # 创建dist和build/output目录
    if not os.path.exists("dist"):
        os.makedirs("dist")
    if not os.path.exists(os.path.join("build", "output")):
        os.makedirs(os.path.join("build", "output"))
    
    # 检查是否存在spec文件
    spec_path = os.path.join("build", "LoLDataCollector.spec")
    if os.path.exists(spec_path):
        # 使用现有的spec文件
        cmd = [
            "pyinstaller",
            "--clean",
            "--workpath", os.path.join("build", "output"),
            spec_path,
        ]
        print("使用已存在的spec文件构建...")
        print(f"Spec文件路径: {spec_path}")
    else:
        # 构建命令
        cmd = [
            "pyinstaller",
            "--name=LoLDataCollector",
            "--workpath", os.path.join("build", "output"),
            "--specpath", "build",
            "--icon=resources/icon.ico" if os.path.exists("resources/icon.ico") else "",
            "--add-data=resources;resources" if os.path.exists("resources") else "",
            "--clean",
        ]
        
        # 是否打包为单文件
        if one_file:
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        
        # 是否显示控制台窗口
        if not console:
            cmd.append("--noconsole")
        
        # 添加主文件
        cmd.append("main.py")
    
    # 过滤空参数
    cmd = [arg for arg in cmd if arg]
    
    print("构建命令:", " ".join(cmd))
    print("正在构建可执行文件，请稍候...")
    subprocess.check_call(cmd)
    
    print("构建完成！")
    print(f"可执行文件位置: {os.path.abspath('dist/LoLDataCollector.exe')}")

def prepare_resources():
    """准备资源文件夹，确保图标等资源可用"""
    # 切换到项目根目录
    os.chdir(ROOT_DIR)
    
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
    # 检查是否有图标文件
    if not os.path.exists("resources/icon.ico"):
        print("警告: 未找到图标文件，将使用默认图标")
        # 尝试生成图标
        create_icon_script = os.path.join("resources", "create_icon.py")
        if os.path.exists(create_icon_script):
            subprocess.call([sys.executable, create_icon_script, os.path.join("resources", "icon.ico")])

def copy_config_template():
    """复制配置模板到dist目录"""
    # 切换到项目根目录
    os.chdir(ROOT_DIR)
    
    if os.path.exists("config_template.py"):
        shutil.copy("config_template.py", "dist/config_template.py")
    elif os.path.exists("config.py"):
        shutil.copy("config.py", "dist/config_template.py")

def create_version_file():
    """创建版本信息文件"""
    # 切换到项目根目录
    os.chdir(ROOT_DIR)
    
    version_info = {
        "version": "1.0.0",
        "build_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "python_version": sys.version,
    }
    
    version_file = os.path.join("build", "version_info.py")
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(f"""# 自动生成的版本信息文件
VERSION = "{version_info['version']}"
BUILD_DATE = "{version_info['build_date']}"
PYTHON_VERSION = "{version_info['python_version']}"
""")
    
    # 复制到项目根目录，供spec文件使用
    shutil.copy(version_file, os.path.join(ROOT_DIR, "version_info.py"))

def main():
    """主函数"""
    print("=" * 50)
    print("LoL游戏数据采集工具构建程序")
    print("=" * 50)
    
    # 确保我们在build目录中运行
    if os.path.basename(os.getcwd()) != "build":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(script_dir) == "build":
            os.chdir(script_dir)
            print(f"已切换工作目录到: {script_dir}")
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("未检测到PyInstaller，需要先安装...")
        install_pyinstaller()
    
    # 准备资源文件
    prepare_resources()
    
    # 创建版本信息
    create_version_file()
    
    # 询问打包选项
    print("\n请选择打包选项:")
    print("1. 单文件模式 (推荐，生成单个exe文件)")
    print("2. 目录模式 (生成包含exe的文件夹)")
    choice = input("请输入选择 (默认1): ").strip()
    one_file = choice != "2"
    
    console = input("是否显示控制台窗口? (y/n, 默认n): ").lower().startswith('y')
    
    # 构建可执行文件
    build_executable(one_file=one_file, console=console)
    
    # 复制配置模板
    copy_config_template()
    
    print("\n构建过程完成!")
    print("您可以在dist目录找到生成的可执行文件。")

if __name__ == "__main__":
    main()
