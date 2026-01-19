import re
import pandas as pd
from datetime import datetime
from openpyxl.utils import escape
import glob
import os


def sanitize_text(text):
    """过滤Excel非法字符（保留中文、英文、常见符号）"""
    # 方法1：移除控制字符（简单方案）
    cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(text))
    
    # 方法2：仅保留允许的字符（更严格）
    # cleaned = re.sub(r'[^\w\u4e00-\u9fa5\s,.!?~@#$%^&*()\-+=，。！？、：；“”‘’…—]', '', str(text))
    
    return cleaned.strip()

def parse_log_to_excel(log_file, excel_file):
    pattern = re.compile(
        r"INFO \|(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\|.*?\|,,"
        r"\|(?P<room_id>\d+) 收到弹幕\s+(?P<user_content>.*)"
    )
    
    data = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line.strip())
            if not match:
                continue

            room_id = match.group("room_id")
            timestamp = datetime.strptime(match.group("time"), "%Y-%m-%d %H:%M:%S.%f")
            
            user_content = match.group("user_content").strip()
            user, content = "未知用户", "无内容"
            
            # 提取用户名和内容（处理格式如 "IO丨OI(99727622)：消息内容"）
            if "：" in user_content:
                user_part, content = user_content.split("：", 1)
                # 提取用户名，去掉ID部分
                user = re.sub(r'\(\d+\)$', '', user_part).strip()
                content = sanitize_text(content)
            
            data.append([room_id, user, content, timestamp])

    if not data:  # 如果没有数据，直接返回
        print(f"No data found in {log_file}")
        return

    df = pd.DataFrame(data, columns=["房间号", "用户", "内容", "时间"])
    df["时间"] = df["时间"].dt.strftime("%Y-%m-%d %H:%M:%S.%f").str[:-3]
    
    # 使用 openpyxl 的 escape 工具二次处理
    df = df.applymap(lambda x: escape.escape(str(x)) if pd.notna(x) else x)
    
    df.to_excel(excel_file, index=False, engine="openpyxl")


def process_log_files(log_dir):
    all_data = []
    # 获取所有日志文件
    log_files = glob.glob(os.path.join(log_dir, 'vspo-live-chat-service*.log*'))
    
    for log_file in log_files:
        parse_log_to_excel(log_file, log_file.replace('.log', '-斗鱼.xlsx'))

if __name__ == '__main__':
    log_dir = '/Users/yinmengqi/Downloads/vspo-live-chat-service'
    process_log_files(log_dir)
