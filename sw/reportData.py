import pymysql
import csv
import json
from datetime import date, datetime

# ===================== 数据库配置（你自己改这里）=====================
DB_CONFIG = {
    "host": "192.144.254.55",       # 数据库地址
    "port": 3306,              # 端口
    "user": "root",            # 用户名
    "password": "xxxxxx",     # 密码
    "database": "swellai_prod",     # 数据库名
    "charset": "utf8mb4"
}

# ===================== 需要查询的 player_id 列表 =====================
PLAYER_IDS = [
    32051
]

# ===================== SQL 查询语句 =====================
SQL_QUERY = """
SELECT
    ard.*,
    wu.wechat_id,
    wu.ai_report_gender
FROM ai_report_data ard 
LEFT JOIN wechat_user wu ON ard.player_id = wu.wechat_id 
WHERE ard.player_id = %s
"""

# ===================== 处理时间格式，解决 JSON 报错 =====================
def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError(f"类型 {type(obj)} 不可序列化")

# ===================== 主逻辑 =====================
def main():
    all_results = []
    
    # 1. 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # 字典格式返回
    
    print(f"开始查询，共 {len(PLAYER_IDS)} 个 player_id...")
    
    # 2. 批量查询
    for pid in PLAYER_IDS:
        cursor.execute(SQL_QUERY, (pid,))
        rows = cursor.fetchall()
        if rows:
            all_results.extend(rows)
            print(f"player_id {pid} → 查询到 {len(rows)} 条")
    
    # 3. 关闭连接
    cursor.close()
    conn.close()
    print(f"\n查询完成！总结果数：{len(all_results)}")

    # 4. 导出 CSV
    if all_results:
        keys = all_results[0].keys()
        with open("result.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_results)
        print("✅ 已导出 result.csv")

    # 5. 导出 JSON（已修复 datetime 问题）
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=json_serial)
    print("✅ 已导出 result.json")

if __name__ == "__main__":
    main()