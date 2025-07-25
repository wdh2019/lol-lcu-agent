# lol_lcu_agent

获取英雄联盟(LOL)对局实时数据和赛后数据的工具

## 项目结构

项目代码已经重构为模块化结构，便于维护和扩展:

- `main.py`: 主程序入口点和状态机逻辑
- `api_client.py`: 处理API请求的客户端
- `lcu_credentials.py`: 获取和验证LCU凭证
- `data_handler.py`: 处理数据保存和目录管理
- `system_utils.py`: 系统工具函数，如进程列表获取

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

- 自动检测游戏状态并采集实时数据
- 在游戏结束后自动获取赛后统计数据
- 数据以JSON格式保存，便于后续分析
- 自动处理LCU凭证，无需手动配置
- 出现权限问题时自动提示并列出系统进程

## 相关资源

### LCU API 文档

https://www.mingweisamuel.com/lcu-schema/tool/#/Plugin%20lol-client-config

### 相关项目

https://github.com/XHXIAIEIN/LeagueCustomLobby?tab=readme-ov-file

## 待办事项

- 未能调通赛后数据接口，需要调试一下lol客户端发现原因
