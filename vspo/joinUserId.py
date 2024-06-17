import pandas as pd

# 读取CSV文件
df = pd.read_csv('/Users/yinmengqi/Desktop/无标题.csv')

# 获取userId列
df['user_id'] = df['user_id'].astype(str)
user_ids = df['user_id'].tolist()

# 每200个userId拼接一次
grouped_user_ids = [','.join(user_ids[i:i+50]) for i in range(0, len(user_ids), 50)]

file = open("/Users/yinmengqi/Desktop/未命名.txt","w")
file.truncate()   #清空文件
# 输出拼接好的字符串
for group in grouped_user_ids:
    file.writelines('----------------------------------------------\n')
    file.writelines(group)
    file.writelines('\n')

file.close()