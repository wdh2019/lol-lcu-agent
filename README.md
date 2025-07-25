# lol_lcu_agent

获取英雄联盟(LOL)对局实时数据和赛后数据的工具

## 项目结构

项目代码已经重构为模块化结构，便于维护和扩展:

- `main.py`: 主程序入口点
- `config.py`: 全局配置项
- `utils/`: 工具函数目录
  - `api_client.py`: 处理API请求的客户端
  - `lcu_credentials.py`: 获取和验证LCU凭证
  - `data_handler.py`: 处理数据保存和目录管理
  - `game_monitor.py`: 游戏监控状态机逻辑
  - `log_uploader.py`: 日志上传功能
  - `system_utils.py`: 系统工具函数，如进程列表获取
  - `config_manager.py`: 配置管理工具
- `ui/`: 图形界面目录
  - `main_window.py`: 主窗口界面实现
  - `base_tab.py`: 标签页基类，包含共用的UI方法
  - `ui_utils.py`: UI通用工具函数
  - `monitor_tab.py`: 游戏监控标签页实现
  - `logs_tab.py`: 日志管理标签页实现
  - `settings_tab.py`: 设置标签页实现

## 使用方法

1. 确保已安装所需依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 以管理员权限运行主程序
   ```bash
   python main.py
   ```

## 功能特点

- 图形界面，易于操作
- 自动检测游戏状态并采集实时数据
- 在游戏结束后自动获取赛后统计数据
- 数据以JSON格式保存，便于后续分析
- 自动处理LCU凭证，无需手动配置
- 可通过界面配置各项参数
- 便捷的日志管理功能
- 出现权限问题时自动提示并列出系统进程

## 配置说明

本工具提供两种配置方式：

1. **通过UI界面配置**: 
   - 点击"设置"标签页，可配置以下参数:
     - LCU API设置 (端口号、令牌等)
     - 日志目录路径
     - 轮询间隔
     - 数据上传设置

2. **直接修改配置文件**:
   - 编辑`config.py`文件，修改相应参数

配置修改后，LCU API和轮询设置将在下次启动监控时生效，日志目录设置立即生效。

## 相关资源

### LCU API 文档

https://www.mingweisamuel.com/lcu-schema/tool/#/Plugin%20lol-client-config

### 相关项目

https://github.com/XHXIAIEIN/LeagueCustomLobby?tab=readme-ov-file
