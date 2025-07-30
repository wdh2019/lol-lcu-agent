# LoL数据收集测试服务器 API 文档

## 概述

本文档描述了LoL数据收集测试服务器的API接口，用于接收和管理英雄联盟游戏数据文件的上传。

**服务器信息**
- 基础URL: `http://localhost:3000`
- 协议: HTTP
- 数据格式: JSON
- 字符编码: UTF-8

---

## 1. 服务状态查询

### GET /

获取服务器当前状态和可用接口信息。

#### 请求参数
无

#### 响应示例
```json
{
  "message": "LoL数据收集测试服务器",
  "status": "running",
  "port": 3000,
  "endpoints": {
    "upload": "/api/upload-logs",
    "list": "/api/files",
    "stats": "/api/stats"
  },
  "timestamp": "2025-07-30 15:30:45"
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 服务器标识信息 |
| status | string | 服务器运行状态 |
| port | number | 监听端口号 |
| endpoints | object | 可用API接口列表 |
| timestamp | string | 服务器当前时间 |

---

## 2. 游戏数据文件上传

### POST /api/upload-logs

接收客户端上传的游戏数据文件。

#### 请求格式
- Content-Type: `multipart/form-data`
- 最大文件大小: 16MB

#### 请求参数

**文件参数:**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 游戏数据JSON文件 |

**表单参数:**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| timestamp | string | 是 | 客户端时间戳 (YYYY-MM-DD HH:MM:SS) |
| file_type | string | 是 | 文件类型，可选值: `live`, `postgame` |
| game_id | string | 是 | 游戏会话ID，通常为时间戳格式 |
| machine_id | string | 是 | 客户端机器唯一标识 |

#### 请求示例 (cURL)
```bash
curl -X POST http://localhost:3000/api/upload-logs \
  -F "file=@data_2025-07-30_15-30-45.json" \
  -F "timestamp=2025-07-30 15:30:45" \
  -F "file_type=live" \
  -F "game_id=2025-07-30_15-30-45" \
  -F "machine_id=a1b2c3d4e5f6g7h8"
```

#### 成功响应 (200)
```json
{
  "message": "文件上传成功",
  "filename": "data_2025-07-30_15-30-45.json",
  "file_type": "live",
  "game_id": "2025-07-30_15-30-45",
  "machine_id": "a1b2c3d4e5f6g7h8",
  "file_size": 15420,
  "json_valid": true,
  "saved_path": "2025-07-30_15-30-45/live/data_2025-07-30_15-30-45.json",
  "server_time": "2025-07-30 15:31:02"
}
```

#### 错误响应

**400 - 请求错误**
```json
{
  "error": "没有文件上传"
}
```

**413 - 文件过大**
```json
{
  "error": "文件太大，最大允许16MB"
}
```

**500 - 服务器错误**
```json
{
  "error": "上传处理出错: 详细错误信息"
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 操作结果消息 |
| filename | string | 保存的文件名 |
| file_type | string | 文件类型 |
| game_id | string | 游戏会话ID |
| machine_id | string | 机器标识 |
| file_size | number | 文件大小（字节） |
| json_valid | boolean | JSON格式是否有效 |
| saved_path | string | 服务器保存路径 |
| server_time | string | 服务器处理时间 |

---

## 3. 文件列表查询

### GET /api/files

获取服务器上所有已上传文件的列表。

#### 请求参数
无

#### 响应示例
```json
{
  "total_files": 5,
  "files": [
    {
      "filename": "data_2025-07-30_15-30-45.json",
      "path": "2025-07-30_15-30-45/live/data_2025-07-30_15-30-45.json",
      "game_id": "2025-07-30_15-30-45",
      "file_type": "live",
      "size": 15420,
      "modified_time": "2025-07-30T15:31:02"
    },
    {
      "filename": "data_2025-07-30_15-35-20.json",
      "path": "2025-07-30_15-30-45/postgame/data_2025-07-30_15-35-20.json",
      "game_id": "2025-07-30_15-30-45",
      "file_type": "postgame",
      "size": 8942,
      "modified_time": "2025-07-30T15:35:20"
    }
  ]
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| total_files | number | 文件总数 |
| files | array | 文件信息列表 |
| files[].filename | string | 文件名 |
| files[].path | string | 相对路径 |
| files[].game_id | string | 游戏会话ID |
| files[].file_type | string | 文件类型 |
| files[].size | number | 文件大小（字节） |
| files[].modified_time | string | 修改时间（ISO格式） |

---

## 4. 上传统计信息

### GET /api/stats

获取文件上传的统计信息。

#### 请求参数
无

#### 响应示例
```json
{
  "total_uploads": 15,
  "by_type": {
    "live": 10,
    "postgame": 5
  },
  "by_machine": {
    "a1b2c3d4e5f6g7h8": 8,
    "x9y8z7w6v5u4t3s2": 7
  },
  "recent_uploads": [
    {
      "upload_time": "2025-07-30T15:31:02.123456",
      "client_timestamp": "2025-07-30 15:30:45",
      "filename": "data_2025-07-30_15-30-45.json",
      "file_type": "live",
      "game_id": "2025-07-30_15-30-45",
      "machine_id": "a1b2c3d4e5f6g7h8",
      "file_size": 15420,
      "file_path": "uploaded_files/2025-07-30_15-30-45/live/data_2025-07-30_15-30-45.json",
      "json_valid": true
    }
  ],
  "upload_folder": "/path/to/uploaded_files"
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| total_uploads | number | 总上传次数 |
| by_type | object | 按文件类型分组统计 |
| by_machine | object | 按机器ID分组统计 |
| recent_uploads | array | 最近10次上传记录 |
| upload_folder | string | 服务器存储目录 |

---

## 5. 文件存储结构

服务器将按以下目录结构存储上传的文件：

```
uploaded_files/
├── 2025-07-30_15-30-45/          # 游戏会话目录
│   ├── live/                     # 实时数据
│   │   ├── data_2025-07-30_15-30-45.json
│   │   ├── data_2025-07-30_15-35-45.json
│   │   └── data_2025-07-30_15-40-45.json
│   └── postgame/                 # 赛后数据
│       └── data_2025-07-30_15-45-20.json
├── 2025-07-30_16-15-30/          # 另一个游戏会话
│   ├── live/
│   └── postgame/
└── upload_log.json               # 上传日志文件
```

---

## 6. 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|------------|----------|------|
| 200 | 成功 | 请求处理成功 |
| 400 | 请求错误 | 缺少必要参数或参数格式错误 |
| 404 | 接口不存在 | 请求的接口路径不存在 |
| 413 | 文件过大 | 上传文件超过16MB限制 |
| 500 | 服务器错误 | 服务器内部处理错误 |

---

## 7. 客户端集成示例

### Python (使用requests库)
```python
import requests

# 上传文件
def upload_game_data(file_path, file_type, game_id, machine_id):
    url = "http://localhost:3000/api/upload-logs"
    
    files = {
        'file': (
            os.path.basename(file_path),
            open(file_path, 'rb'),
            'application/json'
        )
    }
    
    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'file_type': file_type,
        'game_id': game_id,
        'machine_id': machine_id
    }
    
    response = requests.post(url, files=files, data=data)
    files['file'][1].close()
    
    return response.json()
```

### JavaScript (使用fetch API)
```javascript
async function uploadGameData(file, fileType, gameId, machineId) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('timestamp', new Date().toISOString().slice(0, 19).replace('T', ' '));
    formData.append('file_type', fileType);
    formData.append('game_id', gameId);
    formData.append('machine_id', machineId);
    
    const response = await fetch('http://localhost:3000/api/upload-logs', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

---

## 8. 注意事项

1. **文件格式**: 只接受JSON格式的文件
2. **文件大小**: 单个文件最大16MB
3. **字符编码**: 使用UTF-8编码
4. **文件名安全**: 服务器会自动处理文件名安全性
5. **日志记录**: 所有上传操作都会记录到`upload_log.json`
6. **存储限制**: 上传日志只保留最近100条记录
7. **测试环境**: 此服务器仅用于开发测试，不适用于生产环境

---

## 9. 版本信息

- API版本: 1.0
- 文档版本: 1.0
- 最后更新: 2025-07-30
- 维护者: LoL数据收集项目组
