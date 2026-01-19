import pandas as pd

# Function to parse .properties file into a dictionary
def parse_properties(file_path):
    properties = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                key, value = line.split('=', 1)  # Split on the first '='
                properties[key.strip()] = value.strip()
    return properties

# Read the Excel file
excel_file = '/Users/yinmengqi/Downloads/ins多语言国际化分工.xlsx'  # Replace with your Excel file path
df = pd.read_excel(excel_file)

# Read messages_zh.properties file
zh_properties_file = '/Users/yinmengqi/Desktop/i18n/app/messages_zh.properties'  # Replace with your messages_zh.properties file path
zh_properties = parse_properties(zh_properties_file)

# Read messages_en.properties file
en_properties_file = '/Users/yinmengqi/Desktop/i18n/app/messages_en.properties'  # Replace with your messages_en.properties file path
en_properties = parse_properties(en_properties_file)

# Iterate through messages_zh.properties
for code, chinese_name in zh_properties.items():
    # Find the corresponding row in the Excel file
    row = df[df['中文名称'] == chinese_name]
    if not row.empty:
        proofreading_status = row.iloc[0]['校对进度']  # Proofreading status
        proofread_english = row.iloc[0]['英语']  # Proofread English

        # Check if the proofreading status is "已确定" (Confirmed)
        if proofreading_status == '已确定':
            # Get the English value from messages_en.properties
            en_value = en_properties.get(code, '')

            # Compare the proofread English with the English in messages_en.properties
            if proofread_english != en_value:
                print(f"Code: {code}, Chinese: {chinese_name}, English: {en_value}, Proofread English: {proofread_english}")
    else: 
        if '{0}' not in chinese_name:
            print(f"{code}={chinese_name}")