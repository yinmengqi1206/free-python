import requests
import pandas as pd
from datetime import datetime
import time

# ================== 配置参数 ==================
url = "https://jingmeta-app-admin-api.esportsacl.com/feign/ec/adm/comment/page-list"
headers = {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ2c3BvIiwibmJmIjoxNzYwMDc5MDUyLCJleHAiOjIzNjQ4NzksInVzZXJJZCI6MTAwNTksImlhdCI6MTc2MDA3OTA1MiwidXNlcm5hbWUiOiJ5aW5tZW5ncWkifQ.3NAOyYlxpy3l0bTXCTHcWXovNHrcMYikpy7LuxAcR3c",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# 请求参数（动态ID可替换）
params = {
    "column": "createTime",
    "order": "desc",
    "pageNo": 1,
    "pageSize": 1000,  # 每页1000条
    "dynamicId": 1150704,
    "_t": int(time.time() * 1000)  # 当前毫秒时间戳
}

# 存储所有评论数据
all_records = []

# ===================================================
# 开始分页请求
# ===================================================
print("开始获取评论数据...")

while True:
    print(f"正在请求第 {params['pageNo']} 页...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        if not data.get("success"):
            print(f"请求失败，返回信息：{data.get('message')}")
            break

        result = data.get("result", {})
        records = result.get("records", [])
        
        # 添加到总列表
        all_records.extend(records)
        
        total = result.get("total", 0)
        pages = result.get("pages", 1)
        
        print(f"第 {params['pageNo']} 页获取 {len(records)} 条，总计已获取 {len(all_records)} / {total}")
        
        # 判断是否还有下一页
        if params['pageNo'] >= pages:
            break  # 已到最后一页
        
        params['pageNo'] += 1  # 下一页
        time.sleep(0.5)  # 避免请求过快（可适当调整）

    except Exception as e:
        print(f"请求第 {params['pageNo']} 页时发生错误：{e}")
        break

print(f"数据获取完成！共获取到 {len(all_records)} 条评论。")

# ===================================================
# 数据处理并导出 Excel
# ===================================================
if all_records:
    # 转换为 DataFrame
    df = pd.DataFrame(all_records)
    
    # 时间戳转换（毫秒级）
    df['createTime'] = df['createTime'].astype(int)
    df['发布时间'] = pd.to_datetime(df['createTime'], unit='ms', errors='ignore')
    
    # 重命名列（可选）
    df.rename(columns={
        'id': '评论ID',
        'content': '评论内容',
        'fromUserId': '用户ID',
        'fromUserName': '用户名',
        'agreeNum': '点赞数',
        'status': '状态',
        'createTime': '创建时间戳',
        'initStatus': '是否冷启'
    }, inplace=True)
    
    # 只保留需要的列
    export_columns = [
        '评论ID', '评论内容', '发布时间','是否冷启', '点赞数', '状态','用户名', '用户ID'
    ]
    
    # 导出文件名包含动态ID和时间
    filename = f"dynamic_comments_{params['dynamicId']}_{int(time.time())}.xlsx"
    df[export_columns].to_excel(filename, index=False, sheet_name="评论列表")
    
    print(f"✅ 数据已成功导出至：{filename}")
else:
    print("⚠️ 未获取到任何数据，无法导出。")