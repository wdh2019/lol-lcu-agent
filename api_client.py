import requests
import urllib3
import json

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ApiClient:
    """处理API请求的类"""
    
    def __init__(self, live_data_url="https://127.0.0.1:2999/liveclientdata/allgamedata", 
                 lcu_eog_endpoint="/lol-end-of-game/v1/eog-stats-block"):
        """
        初始化API客户端
        
        参数:
            live_data_url: 游戏内实时数据API地址
            lcu_eog_endpoint: LCU赛后数据端点
        """
        self.live_data_url = live_data_url
        self.lcu_eog_endpoint = lcu_eog_endpoint
        
        # 创建一个不验证SSL证书的Session
        self.session = requests.Session()
        self.session.verify = False
        
    def get_live_game_data(self, timeout=2):
        """
        获取游戏内实时数据
        
        参数:
            timeout: 请求超时时间(秒)
            
        返回:
            tuple: (成功标志, 数据/错误信息)
        """
        try:
            response = self.session.get(self.live_data_url, timeout=timeout)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"状态码: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, str(e)
            
    def get_postgame_data(self, port, token, timeout=10):
        """
        获取赛后数据
        
        参数:
            port: LCU端口
            token: LCU认证令牌
            timeout: 请求超时时间(秒)
            
        返回:
            tuple: (成功标志, 数据/错误信息, 内容长度)
        """
        try:
            # 构建LCU API的请求
            eog_url = f"https://127.0.0.1:{port}{self.lcu_eog_endpoint}"
            auth = requests.auth.HTTPBasicAuth('riot', token)
            
            print(f"  请求端点: {self.lcu_eog_endpoint}")
            # 请求赛后数据
            response = self.session.get(eog_url, auth=auth, timeout=timeout)
            
            # 计算响应长度
            content_length = len(response.content) if response.content else 0
            print(f"  响应状态码: {response.status_code}, 数据长度: {content_length} 字节")

            if response.status_code == 200 and content_length > 50:  # 确保有意义的数据
                try:
                    # 尝试解析JSON
                    json_data = response.json()
                    return True, json_data, content_length
                except json.JSONDecodeError as e:
                    print(f"  JSON解析错误: {e}")
                    return False, "返回的内容不是有效的JSON格式", content_length
            else:
                return False, f"响应状态或数据不满足要求 (状态码: {response.status_code})", content_length
                
        except requests.exceptions.ConnectionError as e:
            print(f"  连接错误: {str(e)}")
            return False, f"连接错误: {str(e)}", 0
        except requests.exceptions.Timeout as e:
            print(f"  请求超时: {str(e)}")
            return False, f"请求超时: {str(e)}", 0
        except requests.exceptions.RequestException as e:
            print(f"  请求失败: {str(e)}")
            return False, f"请求失败: {str(e)}", 0
        except Exception as e:
            print(f"  发生未知错误: {str(e)}")
            return False, f"发生未知错误: {str(e)}", 0
