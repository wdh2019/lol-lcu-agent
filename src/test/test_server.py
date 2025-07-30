"""
测试服务端 - 用于模拟接收上传的游戏数据文件
启动在 3000 端口
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploaded_files')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大文件大小

@app.route('/')
def index():
    """首页 - 显示服务状态"""
    return jsonify({
        'message': 'LoL数据收集测试服务器',
        'status': 'running',
        'port': 3000,
        'endpoints': {
            'upload': '/api/upload-logs',
            'list': '/api/files',
            'stats': '/api/stats'
        },
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/upload-logs', methods=['POST'])
def upload_logs():
    """接收上传的游戏数据文件"""
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 收到文件上传请求")
        
        # 检查是否有文件
        if 'file' not in request.files:
            print("错误: 请求中没有文件")
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("错误: 文件名为空")
            return jsonify({'error': '文件名为空'}), 400
        
        # 获取表单数据
        timestamp = request.form.get('timestamp', '')
        file_type = request.form.get('file_type', 'unknown')
        game_id = request.form.get('game_id', 'unknown')
        machine_id = request.form.get('machine_id', 'unknown')
        
        print(f"  文件名: {file.filename}")
        print(f"  文件类型: {file_type}")
        print(f"  游戏ID: {game_id}")
        print(f"  机器ID: {machine_id}")
        print(f"  时间戳: {timestamp}")
        
        # 安全处理文件名
        filename = secure_filename(file.filename)
        if not filename:
            filename = f"data_{int(time.time())}.json"
        
        # 创建以游戏ID和文件类型命名的子文件夹
        save_dir = os.path.join(app.config['UPLOAD_FOLDER'], game_id, file_type)
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(save_dir, filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 尝试解析JSON内容（验证文件格式）
        json_valid = False
        json_data = None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            json_valid = True
            print(f"  JSON格式: 有效 ({len(str(json_data))} 字符)")
        except json.JSONDecodeError as e:
            print(f"  JSON格式: 无效 - {e}")
        except Exception as e:
            print(f"  JSON解析错误: {e}")
        
        # 记录上传信息到日志文件
        log_entry = {
            'upload_time': datetime.now().isoformat(),
            'client_timestamp': timestamp,
            'filename': filename,
            'file_type': file_type,
            'game_id': game_id,
            'machine_id': machine_id,
            'file_size': file_size,
            'file_path': file_path,
            'json_valid': json_valid
        }
        
        log_file = os.path.join(app.config['UPLOAD_FOLDER'], 'upload_log.json')
        upload_logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    upload_logs = json.load(f)
            except:
                upload_logs = []
        
        upload_logs.append(log_entry)
        
        # 只保留最近100条记录
        upload_logs = upload_logs[-100:]
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(upload_logs, f, indent=2, ensure_ascii=False)
        
        print(f"  文件已保存到: {file_path}")
        print(f"  文件大小: {file_size} 字节")
        
        # 返回成功响应
        response_data = {
            'message': '文件上传成功',
            'filename': filename,
            'file_type': file_type,
            'game_id': game_id,
            'machine_id': machine_id,
            'file_size': file_size,
            'json_valid': json_valid,
            'saved_path': os.path.relpath(file_path, app.config['UPLOAD_FOLDER']),
            'server_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = f"上传处理出错: {str(e)}"
        print(f"错误: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """列出所有上传的文件"""
    try:
        files_info = []
        
        # 遍历上传文件夹
        for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
            for file in files:
                if file.endswith('.json') and file != 'upload_log.json':
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])
                    
                    # 从路径解析信息
                    path_parts = relative_path.split(os.sep)
                    if len(path_parts) >= 3:
                        game_id = path_parts[0]
                        file_type = path_parts[1]
                    else:
                        game_id = 'unknown'
                        file_type = 'unknown'
                    
                    file_info = {
                        'filename': file,
                        'path': relative_path,
                        'game_id': game_id,
                        'file_type': file_type,
                        'size': os.path.getsize(file_path),
                        'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    }
                    files_info.append(file_info)
        
        # 按修改时间排序
        files_info.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return jsonify({
            'total_files': len(files_info),
            'files': files_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取文件列表出错: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取上传统计信息"""
    try:
        log_file = os.path.join(app.config['UPLOAD_FOLDER'], 'upload_log.json')
        
        if not os.path.exists(log_file):
            return jsonify({
                'total_uploads': 0,
                'by_type': {},
                'by_machine': {},
                'recent_uploads': []
            }), 200
        
        with open(log_file, 'r', encoding='utf-8') as f:
            upload_logs = json.load(f)
        
        # 统计信息
        total_uploads = len(upload_logs)
        by_type = {}
        by_machine = {}
        
        for log in upload_logs:
            file_type = log.get('file_type', 'unknown')
            machine_id = log.get('machine_id', 'unknown')
            
            by_type[file_type] = by_type.get(file_type, 0) + 1
            by_machine[machine_id] = by_machine.get(machine_id, 0) + 1
        
        # 最近的上传记录
        recent_uploads = upload_logs[-10:] if upload_logs else []
        
        return jsonify({
            'total_uploads': total_uploads,
            'by_type': by_type,
            'by_machine': by_machine,
            'recent_uploads': recent_uploads,
            'upload_folder': app.config['UPLOAD_FOLDER']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息出错: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """文件太大错误处理"""
    return jsonify({'error': '文件太大，最大允许16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def server_error(e):
    """500错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("LoL数据收集测试服务器")
    print("=" * 60)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监听端口: 3000")
    print(f"上传文件夹: {UPLOAD_FOLDER}")
    print("\n可用接口:")
    print("  GET  /                 - 服务状态")
    print("  POST /api/upload-logs  - 上传文件")
    print("  GET  /api/files        - 文件列表")
    print("  GET  /api/stats        - 统计信息")
    print("\n服务器启动中...")
    print("=" * 60)
    
    # 启动Flask服务器
    app.run(
        host='0.0.0.0',  # 监听所有网卡
        port=3000,
        debug=True,
        threaded=True
    )
