import pymysql

conn = pymysql.connect(host='106.14.65.203', user='root',
                       password='Vspn@root123!', database='vspo_ec_app')
cursor = conn.cursor()

# 获取所有文本字段
cursor.execute("""
    SELECT TABLE_NAME, COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'vspo_ec_app' 
      AND DATA_TYPE IN ('varchar','char','text','mediumtext','longtext')
""")

for table, col in cursor.fetchall():
    try:
        sql = f"UPDATE `{table}` SET `{col}` = REPLACE(`{col}`, 'esportsacl.com', 'jingmeta.com') WHERE `{col}` LIKE '%esportsacl.com%'"
        cursor.execute(sql)
        if cursor.rowcount > 0:
            print(f"Updated {cursor.rowcount} rows in {table}.{col}")
    except Exception as e:
        print(f"Error on {table}.{col}: {e}")

conn.commit()
conn.close()
