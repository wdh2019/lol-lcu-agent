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

## 测试服务端

### 文件说明

- `test_server.py` - Flask测试服务端，模拟接收上传的游戏数据文件
- `start_test_server.bat` - Windows启动脚本，自动安装依赖并启动服务器
- `test_upload_client.py` - 测试客户端，用于测试文件上传功能
- `requirements_test_server.txt` - 测试服务端的Python依赖

### 使用步骤

#### 1. 启动测试服务器

双击运行 `start_test_server.bat` 或在命令行中执行：

```cmd
cd src/test
start_test_server.bat
```

服务器将启动在 `http://localhost:3000`

#### 2. 运行测试客户端

在另一个命令行窗口中运行：

```cmd
cd src/test
python test_upload_client.py
```

### 服务器接口

测试服务器提供以下接口：

- **GET /**: 获取服务器状态
- **POST /api/upload-logs**: 接收上传的游戏数据文件
- **GET /api/files**: 获取所有上传文件的列表
- **GET /api/stats**: 获取上传统计信息

### 上传文件存储

上传的文件会按以下结构存储：

```
src/test/uploaded_files/
├── 2025-07-30_15-30-45/          # 游戏ID目录
│   ├── live/                     # 实时数据
│   │   └── data_xxx.json
│   └── postgame/                 # 赛后数据
│       └── data_zzz.json
└── upload_log.json               # 上传日志
```
