import os
image_list = {}
# 图片文件夹和动态对应关系
dynamic_dict = {
'013':146,
'014':147,
'049':148,
'059':149,
'061':150
}


base_path = '/Users/yinmengqi/Desktop/dynamic/'
cdn = 'https://cdn.vspo.cn/ins-app/userImage/prod/init/%E5%8A%A8%E6%80%81/'

for root, dirs, files in os.walk(base_path+'动态/'):
    # 循环文件
    for file in files:
        dir = root.replace(base_path+'动态/','')
        if dir == '':
            continue
        if file == '.DS_Store':
            continue
        
        try:
            dynamic_dict[dir]
        except:
            continue
        
        url = os.path.join(cdn+dir,file)
        dynamic_id = dynamic_dict[dir]
        formatted_sql = f"""INSERT INTO `vspo_ins_app`.`ins_app_dynamic_ext` (`dynamic_id`, `ext_type`, `ext_content`) 
        VALUES ({dynamic_id}, 0, '{url}');"""
        print(formatted_sql)