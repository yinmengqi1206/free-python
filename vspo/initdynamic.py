import pandas as pd
import random
import os

def select_random_user_by_sex(user_list, sex,user_id):
    if user_id is not None:
        filtered_list = [user for user in user_list if user['id'] == user_id]
    elif sex == '男':
        filtered_list = [user for user in user_list if user['sex'] == 0]
    elif sex == '女':
        filtered_list = [user for user in user_list if user['sex'] == 1]
    else:
        filtered_list = user_list
    
    if filtered_list:
        return random.choice(filtered_list)
    else:
        return None

base_path = '/Users/yinmengqi/Desktop/dynamic/'


# 读取 文件user.xls
user = pd.read_excel(base_path+'user.xls')
user_list = []
for index, row in user.iterrows():
    user_list.append(row)



# 读取Excel文件
dynamic = pd.read_excel(base_path+'INS新乐园冷启动数据导入模板.xlsx')

# 打印每一行的内容，跳过包含'003'或'004'的行
for index, row in dynamic.iterrows():
    user_id = row['发布用户手机号']
    # 调用函数并传入参数
    if pd.isna(user_id):
        selected_user = select_random_user_by_sex(user_list, row['发布用户性别'],None)
    else:
        selected_user = select_random_user_by_sex(user_list, row['发布用户性别'],user_id)
    user_id = selected_user['id']
    phone = selected_user['phone']
    content = row['发布内容']
    tagid = row['标签关联邀请函/活动ID（邀请函可标注是哪个店的邀请函，活动从现有活动的ID进行关联）']
    time = pd.to_datetime(row['发布时间（YYYY-MM-DD HH:mm:ss）'])
    if row['标签类型（0邀请函，1活动）']==1:
        tagtype = 1
        continue
    if row['标签类型（0邀请函，1活动）']==0:
        tagtype = 0
    else: 
        tagid = 'nan'
        tagtype = 'nan'
        continue

    formatted_sql = f"""INSERT INTO `vspo_ins_app`.`ins_app_dynamic` (`user_id`, `phone`, `content`, `status`, `check_status`, `tag_type`, `tag_id`, `create_time`) 
        VALUES ('{user_id}', '{phone}', '{content}', 0, 1, {tagtype}, '{tagid}', '{time}');"""
    formatted_sql = formatted_sql.replace("'NaT'",'now()').replace("'nan'",'null').replace("nan",'null')
    print(formatted_sql)
