import redis
import pymysql
import openpyxl
from openpyxl import Workbook

def get_user_ids_from_redis(redis_host,redis_password, redis_port, redis_db, key_prefixes):
    # 连接 Redis
    redis_client = redis.StrictRedis(host=redis_host,password=redis_password, port=redis_port, db=redis_db, decode_responses=True)
    
    # 收集所有匹配的用户 ID
    user_ids = set()
    for prefix in key_prefixes:
        keys = redis_client.keys(f"{prefix}*")
        print(f"找到前缀 {prefix} 的键：{keys}")
        for key in keys:
            zset_data = redis_client.zrevrange(key, 0, -1)  # 获取 zset 的 member 值
            user_ids.update(zset_data)
    
    print(f"从 Redis 获取到的总用户 ID 数量：{len(user_ids)}")
    return list(user_ids)

def query_users_from_mysql(mysql_config, user_ids):
    if not user_ids:
        print("没有用户 ID，无需查询 MySQL。")
        return []
    
    # 构造 SQL 查询
    query = f"""
    SELECT nick_name, phone 
    FROM ins_user 
    WHERE id IN ({','.join(['%s'] * len(user_ids))})
    """
    
    # 连接 MySQL 并执行查询
    connection = pymysql.connect(**mysql_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, user_ids)
            results = cursor.fetchall()
            print(f"从 MySQL 获取到的记录数量：{len(results)}")
            return results
    finally:
        connection.close()

def export_to_excel(data, output_file):
    # 创建 Excel 工作簿
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "User Data"
    
    # 写入标题行
    sheet.append(["Nickname", "Phone"])
    
    # 写入数据
    for row in data:
        sheet.append(row)
    
    # 保存 Excel 文件
    workbook.save(output_file)
    print(f"数据已导出到 {output_file}")

if __name__ == "__main__":
    # Redis 配置
    REDIS_HOST = "r-uf6onbubupygr7x0yipd.redis.rds.aliyuncs.com"
    REDIS_PASSWORD = "xxxxxxx"
    REDIS_PORT = 6379
    REDIS_DB = 1
    KEY_PREFIXES = ["ins-app:rank:1", "ins-app:rank:2"]  # 键前缀集合

    # MySQL 配置
    MYSQL_CONFIG = {
        "host": "rm-uf6821gf44bi8ekt6fo.mysql.rds.aliyuncs.com",
        "user": "root",
        "password": "xxxxxxx",  # 修改为你的 MySQL 密码
        "database": "vspo_ins",  # 修改为你的数据库名
        "port": 3306,
        "charset": "utf8mb4"
    }
    
    # 输出文件名
    OUTPUT_FILE = "user_data.xlsx"
    
    # 获取 Redis 中的用户 ID 列表
    user_ids = get_user_ids_from_redis(REDIS_HOST,REDIS_PASSWORD, REDIS_PORT, REDIS_DB, KEY_PREFIXES)
    
    # 使用用户 ID 列表查询 MySQL
    user_data = query_users_from_mysql(MYSQL_CONFIG, user_ids)
    
    # 将查询结果导出到 Excel
    export_to_excel(user_data, OUTPUT_FILE)
