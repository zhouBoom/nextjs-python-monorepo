from flask import Flask, jsonify
import requests
import json
from datetime import datetime
import threading
import time
import os
from flask_cors import CORS  # 安装：pip install flask-cors

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 添加这行
# 配置参数
COOKIE = "xxoo-tmp=zhHans; sid=xxxxx; token=yyyyy"  # 替换真实Cookie
BASE_URL = "https://prod-web.cloudgn.com/qs_svc/v1/list_stock_auction_score"
DATA_FILE = "data.json"

def fetch_stock_data():
    """定时数据获取线程"""
    while True:
        try:
            response = requests.post(
                BASE_URL,
                json={
                    "min_score": 0,
                    "max_score": 288,
                    "trade_date": datetime.now().strftime("%Y-%m-%d"),
                    "page_num": 1,
                    "page_size": 50,
                    "_t": int(time.time() * 1000)
                },
                headers={"Cookie": COOKIE},
                timeout=10  # 添加超时设置
            )
            print(response.status_code)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200 and data.get('result', {}).get('list'):
                    # 数据校验后写入文件
                    processed = []
                    for item in data['result']['list']:
                        try:
                            processed.append({
                                "code": item["stock_code"].split(".")[0],
                                "name": item["stock_name"],
                                "score": int(item["total_score"]),
                                "change": float(item["change_rate"]),
                                "open_rise": float(item["open_rise"]),
                                "price": float(item["trade"])
                            })
                        except KeyError as e:
                            print(f"数据字段缺失: {str(e)}，原始数据: {item}")
                    print("写入数据1", processed)
                    # 确保写入目录存在
                    # os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
                    with open(DATA_FILE, 'w', encoding='utf-8') as f:
                        json.dump(processed, f, ensure_ascii=False, indent=2)
                    # with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    #     print('写入数据2')
                        # json.dump(processed, f, ensure_ascii=False, indent=2)
                else:
                    print(f"API返回异常: {data.get('message', '未知错误')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"数据更新异常: {str(e)}")
        
        time.sleep(300)  # 每5分钟更新

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """数据接口"""
    try:
        if not os.path.exists(DATA_FILE):
            print("123")
            return jsonify({"error": "数据文件不存在"}), 500
            
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(data)
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 启动前检查Cookie有效性
    if not COOKIE or '=' not in COOKIE:
        raise ValueError("无效的Cookie格式，请检查配置")
    
    # 启动定时任务线程
    thread = threading.Thread(target=fetch_stock_data, daemon=True)
    thread.start()
    
    # 启动Flask服务
    app.run(
        host='0.0.0.0',
        port=3838,
        threaded=True  # 启用多线程处理
    )