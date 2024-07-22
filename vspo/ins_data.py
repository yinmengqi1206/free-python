#!/usr/bin/env python
# -*- utf-8 -*-
import datetime
import logging
import smtplib
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import mysql.connector
import pandas as pd

# 指定SQL文件所在的目录
# 服务器的路径
base_directory = '/data/project-service/ins_app_data/'
# 本地调试路径
# base_directory = './'
# MySQL数据库连接配置
mysql_config = {
    # 内网地址
    'host': 'rm-uf6821gf44bi8ekt6.mysql.rds.aliyuncs.com',
    # 外网地址
    # 'host': 'rm-uf6821gf44bi8ekt6fo.mysql.rds.aliyuncs.com',
    'port': 3306,
    'database': 'vspo_ins_app',
    'user': 'root',
    'password': '******'
}


def create_directory(directory):
    """
    创建目录
    :param directory:
    :return:
    """
    path = Path(directory)
    if not path.exists():
        path.mkdir(parents=True)
        print(f"目录 {directory} 创建成功！")
    else:
        print(f"目录 {directory} 已存在！")


create_directory(base_directory)
# 配置日志记录
logging.basicConfig(filename=base_directory + 'ins_data.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

today = datetime.datetime.now()
today_str = today.strftime('%Y-%m-%d')
today_time_str = today.strftime('%Y-%m-%d-%H-%M-%S')

# 发送邮件配置
email_config = {
    # 发件人昵称和地址
    'sender': 'ins新乐园app<monitor@vspo.cn>',
    # 收件人昵称和地址 多个收件人用逗号分隔
    'receiver': 'mengqingwei@vspo.cn,jiajie@vspo.cn,yanglei@vspo.cn,tongxin@vspo.cn,yinmengqi@vspo.cn',
    # 邮件主题
    'subject': 'ins新乐园app数据',
    # 邮件内容
    'body': 'ins新乐园app数据',
    # 邮件服务器
    'smtp_server': 'smtp.exmail.qq.com',
    # 邮件端口
    'smtp_port': 465,
    # 邮件发送方名称
    'username': 'monitor@vspo.cn',
    # 邮件发送方密码
    'password': 'pbNvmkyN2VbQ4qtn'
}


def run_data():
    """
    根据数据库表中的sql查询数据
    把查询的数据生成excel
    把excel通过邮件发送出去
    :return:
    """
    base_today_path = base_directory + today_str + "/"
    create_directory(base_today_path)
    # 所有excel的名字
    excel_name_list = []
    # 所有excel文件对应的记录数
    excel_count_list = []
    # 内容
    excel_content_list = []
    # 英文换行
    flag = "\n"
    # SQL查询语句
    sql_query = """
        SELECT
            idq.id,
            idq.file_name,
            idq.file_sql 
        FROM
            ins_data_sql idq 
        WHERE
            idq.file_status = 1
    """
    # 查询语句要执行的sql
    results_column, results = query_data(sql_query)
    # 生成Excel文件
    start_time = time.time()
    logging.info('生成Excel文件开始:{} s'.format(start_time))
    for row in results:
        file_name = row[1]
        file_sql = row[2]
        logging.info('开始生成' + file_name)
        # 生成Excel文件
        excel_file = file_name + '.xlsx'
        # 执行SQL语句
        row_column, row_result = query_data(file_sql)
        # 加入excel列表名字
        excel_name_list.append(excel_file)
        # content
        excel_count_list.append(len(row_result))
        # 内容
        if(excel_file.find("汇总数据")!=-1):
            content = ""
            for index,row in enumerate(row_column):
                content = content + "     - "+str(row) + "：" + str(row_result[0][index]) + flag
            excel_content_list.append(content)
        else:
            excel_content_list.append("")
        # 将查询结果转换为DataFrame
        general_excel(row_column, row_result, base_today_path + excel_file)
    end_time = time.time()
    logging.info('生成Excel文件结束:{} s,耗时:{} s'.format(end_time, end_time - start_time))

    start_time = time.time()
    logging.info('邮件生成配置生开始:{} s'.format(start_time))
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = email_config['sender']
    msg['To'] = email_config['receiver']
    msg['Subject'] = email_config['subject'] + "-" + today_str

    # 添加附件
    for excel_file, excel_count,content in zip(excel_name_list, excel_count_list,excel_content_list):
        with open(base_today_path + excel_file, 'rb') as file:
            attachment = MIMEApplication(file.read())
        attachment.add_header('Content-Type', 'application/octet-stream')
        attachment.add_header('Content-Disposition', 'attachment', filename=Header(excel_file, 'utf-8').encode())
        msg.attach(attachment)
		# 拼接邮件内容
        if(excel_file.find("汇总数据")!=-1):
            email_config['body'] = email_config['body'] + flag + excel_file + ":" + flag + content
        else:
            email_config['body'] = email_config['body'] + flag + excel_file + "条数：" + str(excel_count)
    # 添加邮件正文
    msg.attach(MIMEText(email_config['body'], 'plain', 'utf-8'))

    end_time = time.time()
    logging.info('邮件生成配置结束:{} s,耗时:{} s'.format(end_time, end_time - start_time))
    # 发送邮件
    send_email(msg)


def send_email(msg):
    """
    发送邮件
    :param msg:
    :return:
    """

    try:
        start_time = time.time()
        logging.info('邮件发送开始:{} s'.format(start_time))
        # 创建SMTP服务器
        server = smtplib.SMTP_SSL(email_config['smtp_server'], email_config['smtp_port'])
        # 登录SMTP服务器
        server.login(email_config['username'], email_config['password'])
        # 发送邮件
        server.send_message(msg)
        # 退出SMTP服务器
        server.quit()
        # 打印日志
        end_time = time.time()
        logging.info('邮件发送结束:{} s,耗时:{} s'.format(end_time, end_time - start_time))
    except Exception as e:
        # 打印错误日志
        logging.error('邮件发送失败: %s', str(e))


def general_excel(column, result, excel_file):
    """
    生成excel
    :param column:
    :param result:
    :param excel_file:
    :return:
    """
    start_time = time.time()
    logging.info('excel生成开始:{} s'.format(start_time))
    df = pd.DataFrame(result, columns=column)
    df.to_excel(excel_file, index=False)
    end_time = time.time()
    logging.info('excel生成结束:{} s,耗时:{} s'.format(end_time, end_time - start_time))


def query_data(sql_query):
    """
    查询数据
    :param sql_query:
    :return:
    """
    start_time = time.time()
    logging.info('sql查询开始:{} s'.format(start_time))
    # 连接MySQL数据库
    conn = mysql.connector.connect(**mysql_config)
    # 执行SQL查询
    cursor = conn.cursor()
    cursor.execute(sql_query)
    # 获取查询结果
    result = cursor.fetchall()
    column_names = cursor.column_names
    # 关闭数据库连接
    cursor.close()
    conn.close()
    end_time = time.time()
    logging.info('sql查询结束:{} s,耗时:{} s'.format(end_time, end_time - start_time))
    return column_names, result


if __name__ == '__main__':
    logging.info('开始日期：{}##################################################'.format(
        today_time_str))
    run_data()
    logging.info('结束日期：{}##################################################'.format(
        today_time_str))
    exit(0)
