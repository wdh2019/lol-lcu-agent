# 测试脚本

这个目录包含了用于测试和调试各个功能的脚本。

## 可用脚本

1. **test_monitor.py** - 直接启动游戏监控功能
   ```
   python test_monitor.py
   ```

2. **test_upload.py** - 测试游戏日志上传功能
   ```
   # 交互式选择要上传的游戏
   python test_upload.py
   
   # 直接指定要上传的游戏文件夹
   python test_upload.py 2025-07-25_12-23-44
   ```

3. **test_utils.py** - 测试各个工具函数
   ```
   # 显示帮助信息
   python test_utils.py --help
   
   # 测试API客户端
   python test_utils.py --api
   
   # 测试LCU凭证获取
   python test_utils.py --lcu
   
   # 测试数据处理器
   python test_utils.py --data
   
   # 测试系统工具
   python test_utils.py --sys
   
   # 测试所有功能
   python test_utils.py --all
   ```

4. **test_lcu_credentials.py** - 测试LCU凭证获取功能

## 使用说明

### test_lcu_credentials.py

确保英雄联盟客户端正在运行，然后执行:
```bash
python -m test.test_lcu_credentials
```

预期输出:
- 获取到的端口和令牌信息
- 连接测试结果
- 各个API端点的可用性测试结果

## 注意事项

- 这些测试脚本仅用于开发和调试目的
- 要使用完整的功能，请通过主程序启动UI界面：`python main.py`

## 故障排除

如果遇到问题:
1. 确保英雄联盟客户端已经启动（测试LCU功能时）
2. 检查是否以管理员权限运行命令提示符
3. 验证是否已安装所需的Python库，特别是PyQt5和requests
