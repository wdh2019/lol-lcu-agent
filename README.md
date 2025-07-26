# lol_lcu_agent

获取英雄联盟(LOL)对局实时数据和赛后数据的工具

## 项目结构

项目代码采用模块化结构，便于维护和扩展:

- `main.py`: 主程序入口点，负责启动图形界面
- `build_exe.bat`: 构建脚本，运行后可以构建整个项目。可执行文件会产出到dist目录下
- `src/`: 源代码目录
  - `__init__.py`: 包初始化文件
  - `config.py`: 全局配置项，所有默认配置的集中管理
  - `utils/`: 工具函数目录
    - `__init__.py`: 包初始化文件
    - `api_client.py`: 处理 API 请求的客户端类
    - `lcu_credentials.py`: 获取和验证 LCU 凭证的功能模块
    - `data_handler.py`: 数据保存和目录管理类
    - `game_monitor.py`: 游戏监控状态机核心逻辑
    - `log_uploader.py`: 日志上传功能模块
    - `config_manager.py`: 配置管理类，负责配置的读取和保存
    - `system_utils.py`: 系统工具函数，如进程列表获取等
  - `ui/`: 图形界面目录
    - `__init__.py`: 包初始化文件
    - `main_window.py`: 主窗口界面实现
    - `base_tab.py`: 标签页基类，包含共用的 UI 方法
    - `ui_utils.py`: UI 通用工具函数
    - `monitor_tab.py`: 游戏监控标签页实现
    - `logs_tab.py`: 游戏数据管理标签页实现
    - `settings_tab.py`: 设置标签页实现
  - `test/`: 测试目录
    - `__init__.py`: 包初始化文件
    - `test_lcu_credentials.py`: LCU 凭证相关测试
    - `test_monitor.py`: 游戏监控相关测试
    - `test_upload.py`: 日志上传相关测试
    - `test_utils.py`: 工具函数相关测试
- `build/`: 构建相关文件目录
  - `build.py`: 构建脚本
  - `build.bat`: Windows 一键构建脚本
  - `LoLDataCollector.spec`: PyInstaller 配置文件
- `resources/`: 资源文件目录
  - `create_icon.py`: 创建应用图标的脚本

## 使用方法

### 源码运行

1. 确保已安装所需依赖

   ```bash
   pip install -r requirements.txt
   ```

2. 以管理员权限运行主程序

   ```bash
   python main.py
   ```

3. 可选的命令行参数:
   ```bash
   python main.py --help  # 显示帮助信息
   ```

### 可执行文件

1. 构建可执行文件

   ```bash
   cd build
   build.bat
   ```

   或

   ```bash
   cd build
   python build.py
   ```

2. 在 dist 目录中找到生成的 LoLDataCollector.exe，双击运行
   > 注意：首次运行可能需要以管理员权限运行

## TODO

- live数据采集时，实际间隔时间会比设置的间隔时间多2秒左右
- 目前游戏数据全部保存在用户本地，需要替换实际的上传接口url


## 构建说明

本项目支持构建为 Windows 可执行文件(.exe)，方便分发和使用。

### 构建步骤

1. 在 Windows 系统下，双击运行项目根目录下的`build_exe.bat`文件即可一键构建

   或者手动执行以下步骤：

   a. 安装必要的依赖：

   ```bash
   pip install -r requirements.txt
   ```

   b. 运行构建脚本：

   ```bash
   python build/build.py
   ```

2. 按照提示选择打包方式：

   - 单文件模式：生成单个 exe 文件，便于分发
   - 目录模式：生成包含 exe 的文件夹，启动速度更快

3. 构建完成后，可执行文件将保存在`dist`目录中

### 注意事项

- 打包后的程序首次运行可能需要以管理员权限运行
- 若遇到防病毒软件报警，可添加信任或例外
- 可执行文件体积较大是正常现象，因为它包含了 Python 运行环境和所有依赖

## 配置说明

本工具提供两种配置方式：

1. **通过 UI 界面配置**:

   - 点击"设置"标签页，可配置以下参数:
     - LCU API 设置 (端口号、令牌等)
     - 日志目录路径
     - 轮询间隔
     - 数据上传设置

2. **直接修改配置文件**:
   - 编辑`src/config.py`文件，修改相应参数

配置修改后，LCU API 和轮询设置将在下次启动监控时生效，日志目录设置立即生效。

### 依赖注入和配置管理

项目采用依赖注入设计模式：

- `ConfigManager`类负责集中管理所有配置项
- 配置项通过参数传递给需要它们的模块，而不是通过直接导入
- UI 组件通过父组件获取配置，实现了一致的配置访问方式
- 工具类通过构造函数或函数参数接收配置，降低了模块间耦合

## 相关资源

### LCU API 文档

https://www.mingweisamuel.com/lcu-schema/tool/#/Plugin%20lol-client-config

### 开发注意事项

1. **配置管理**：使用 `ConfigManager` 类访问配置，而不是直接导入配置模块
2. **依赖注入**：通过构造函数或函数参数传递依赖，而不是在多处直接导入
3. **UI 组件继承**：所有 UI 标签页都应继承 `BaseTab` 类
4. **异常处理**：使用 try-except 块处理可能的异常，并提供有用的错误信息

### 相关项目

https://github.com/XHXIAIEIN/LeagueCustomLobby?tab=readme-ov-file
