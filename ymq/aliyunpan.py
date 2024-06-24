from aligo import Auth,Aligo

ali = Aligo()
# auth = Auth(name='refresh_token', refresh_token='3ba53ed6073141298eea224f531b9400')

# 下面这一丢丢代码意思是，查询阿里云盘的文件列表，然后替换名字，然后改名
# 获取网盘目录文件列表
file_list = ali.get_file_list("63e612293381968b5d7c4ed29243a98b68aa9e34")
# 循环
for file in file_list:
    # print(file)
    # 替换（replace）’第‘为’.S01.E‘,截取0-12位（代码里一般是从0开始）,再拼一个mp4
    # 不良人 第01集.mp4==》不良人.S01.E01.mp4
    newname = file.name.replace(" 第",".S01.E")[0:12]+'.mp4'
    # 打印出来，可以看看改成了啥
    print(newname)
    # 根据file_id替换名字
    ali.rename_file(file.file_id,newname)