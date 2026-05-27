import pandas as pd
import json
from typing import Dict, List, Any

TARGET_HAND = "左手"

def normalize_hand(hand_value: Any) -> str:
    """
    统一手型写法，兼容 左/右/左手/右手/不区分。
    """
    if pd.isna(hand_value):
        return ""

    hand = str(hand_value).strip()
    hand_map = {
        "左": "左手",
        "右": "右手",
        "左手": "左手",
        "右手": "右手",
        "不区分": "不区分",
    }
    return hand_map.get(hand, hand)

def load_positioning_data(position_file: str, target_hand: str = TARGET_HAND) -> Dict[str, List[Dict]]:
    """
    读取学生站位数据，返回以 plan_number 为 key 的 student-positioning 映射。
    同一编号下优先使用目标手型，其次使用“不区分”。
    """
    target_hand = normalize_hand(target_hand)
    hand_priority = {target_hand: 2, "不区分": 1}
    positioning_data = {}

    try:
        with open(position_file, "r", encoding="utf-8") as file:
            rows = json.load(file)
    except FileNotFoundError:
        print(f"提示: 找不到站位文件 '{position_file}'，将跳过 student-positioning")
        return positioning_data
    except json.JSONDecodeError as e:
        print(f"解析站位文件失败: {position_file}, 错误: {e}")
        return positioning_data

    for row in rows:
        plan_number = row.get("编号")
        if plan_number is None:
            continue

        hand = normalize_hand(row.get("手"))
        if hand not in hand_priority:
            continue

        student_positioning = row.get("student-positioning", [])
        if not student_positioning:
            continue

        plan_key = str(int(plan_number))
        current = positioning_data.get(plan_key)
        if current is None or hand_priority[hand] > current["priority"]:
            positioning_data[plan_key] = {
                "priority": hand_priority[hand],
                "student-positioning": student_positioning,
            }

    return {
        plan_number: data["student-positioning"]
        for plan_number, data in positioning_data.items()
    }

def parse_parameters(row_value: str, machine_type: str) -> tuple:
    """
    解析单元格中的参数字符串，返回 (point列表, rate值)。
    根据机器类型（普尚或SBAS）处理不同的参数格式。
    
    SBAS格式: "速度45；左右30；上下60；频率40"
    普尚格式: "左右1400；上下4400；速度150；频率4"
    多点位格式:
        "频率45
         点1
         速度65；左右40；上下60

         点2
         速度23；左右56；上下54"
    """
    import re
    
    points = []
    rate = None
    
    if pd.isna(row_value) or not str(row_value).strip():
        return [], None
    
    row_value = str(row_value).strip()
    
    try:
        # 提取频率（rate）- 支持小数如3.5、4.5
        rate_match = re.search(r'频率([\d.]+)', row_value)
        rate = float(rate_match.group(1)) if rate_match else None

        def parse_point(point_text: str) -> Dict[str, int] | None:
            # 提取速度（speed）
            speed_match = re.search(r'速度(\d+)', point_text)
            speed = int(speed_match.group(1)) if speed_match else 0

            # 提取左右（lr）
            lr_match = re.search(r'左右(\d+)', point_text)
            lr = int(lr_match.group(1)) if lr_match else 0

            # 提取上下（ud）
            ud_match = re.search(r'上下(\d+)', point_text)
            ud = int(ud_match.group(1)) if ud_match else 0

            if speed or lr or ud:  # 至少有一个参数
                return {"lr": lr, "ud": ud, "speed": speed}
            return None

        point_matches = list(re.finditer(r'点\s*\d+', row_value))

        if point_matches:
            for index, point_match in enumerate(point_matches):
                start = point_match.end()
                end = point_matches[index + 1].start() if index + 1 < len(point_matches) else len(row_value)
                point = parse_point(row_value[start:end])
                if point:
                    points.append(point)
        else:
            point = parse_point(row_value)
            if point:
                points.append(point)
    
    except Exception as e:
        print(f"解析参数失败: {row_value}, 错误: {e}")
    
    return points, rate

def process_sheet(sheet_df: pd.DataFrame, key_name: str) -> Dict[str, List[Dict]]:
    """
    处理单个Sheet，返回以 plan_number 为 key 的参数映射。
    """
    plan_data = {}
    
    # 处理合并单元格索引（Pandas读取时合并单元格下方为空，需填充）
    # 使用较新的pandas API
    sheet_df = sheet_df.ffill()
    
    for _, row in sheet_df.iterrows():
        plan_number = str(int(row['编号'])) if pd.notna(row['编号']) else None
        handedness = normalize_hand(row['持拍手区分'])
        
        if not plan_number or plan_number == 'nan':
            continue
            
        # 仅处理目标手型或“不区分”的数据
        if handedness not in [TARGET_HAND, '不区分']:
            continue
            
        # 构建 difficulty 1, 2, 3 的数据
        difficulties = []
        
        # 获取参数列（难度低、默认、高）
        param_cols = ['参数-难度（低）', '参数-难度（默认）', '参数-难度（高）']
        
        for difficulty_level, col in enumerate(param_cols, start=1):
            if col not in sheet_df.columns:
                continue
                
            cell_text = row[col]
            
            # 解析参数，获取 points 和 rate
            points, rate = parse_parameters(cell_text, key_name)
            
            # 如果没有解析到rate，使用默认映射
            if rate is None:
                rate_map = {1: 50, 2: 40, 3: 30}  # 默认频率映射
                rate = rate_map.get(difficulty_level, 40)
            
            if points:  # 只有有效的参数才添加
                difficulties.append({
                    "difficulty": difficulty_level,
                    "rate": rate,
                    "point": points
                })
        
        # 存储到结果中
        if plan_number not in plan_data:
            plan_data[plan_number] = []
            
        # 查找是否已有该编号的配置，如果有则更新对应key，没有则添加
        existing = next((item for item in plan_data[plan_number] if key_name in item), None)
        if existing:
            existing[key_name] = difficulties
        else:
            if difficulties:  # 只有有难度数据才添加
                plan_data[plan_number].append({key_name: difficulties})
    
    return plan_data

def generate_sql_and_json(
    legacy_df: pd.DataFrame,
    spoball_df: pd.DataFrame,
    positioning_data: Dict[str, List[Dict]] | None = None,
):
    """
    主函数：生成JSON数据并输出SQL语句。
    """
    # 处理普尚数据
    legacy_data = process_sheet(legacy_df, "legacy-pb")
    print(f"普尚数据处理完成，包含 {len(legacy_data)} 个plan_number")
    
    # 处理SBAS数据
    spoball_data = process_sheet(spoball_df, "spoball-v1")
    print(f"SBAS数据处理完成，包含 {len(spoball_data)} 个plan_number")

    if positioning_data is None:
        positioning_data = {}
    print(f"学生站位数据处理完成，包含 {len(positioning_data)} 个plan_number")
    
    # 合并数据并生成SQL
    # 获取所有涉及的 plan_number
    all_plans = set(legacy_data.keys()).union(set(spoball_data.keys())).union(set(positioning_data.keys()))
    print(f"总共需要生成SQL的plan_number: {len(all_plans)}")
    
    if len(all_plans) == 0:
        print("警告: 没有找到任何数据，请检查:")
        print("  1. Excel文件的Sheet名称是否正确")
        print("  2. 数据中是否有'编号'列")
        print("  3. 数据是否正确解析")
        return
    
    for plan_number in sorted(all_plans):
        final_json_obj = {}
        
        # 合并普尚数据
        if plan_number in legacy_data:
            # 注意：process_sheet 返回的结构可能需要调整以匹配 legacy_data[plan_number] 是列表
            # 这里假设 legacy_data[plan_number] 是包含 {"legacy-pb": [...]} 的列表
            for item in legacy_data[plan_number]:
                final_json_obj.update(item)
                
        # 合并SBAS数据
        if plan_number in spoball_data:
            for item in spoball_data[plan_number]:
                final_json_obj.update(item)

        # 合并学生站位数据，与 legacy-pb、spoball-v1 同级
        if plan_number in positioning_data:
            final_json_obj["student-positioning"] = positioning_data[plan_number]
        
        # 只有当有实际数据时才生成SQL
        if not final_json_obj:
            print(f"跳过 plan_number={plan_number}（没有有效的参数数据）")
            continue
        
        # 转换为字符串
        json_str = json.dumps(final_json_obj, ensure_ascii=False, separators=(',', ':'))
        
        # 生成SQL
        if(TARGET_HAND == "左手"):
            sql = f"UPDATE `training_plan` SET `ball_machine_left` = '{json_str}' WHERE `plan_number` = {plan_number};"
        else:
            sql = f"UPDATE `training_plan` SET `ball_machine_right` = '{json_str}' WHERE `plan_number` = {plan_number};"
        print(sql)

if __name__ == "__main__":
    # 读取Excel文件
    import os
    
    # 相对于脚本文件的路径，确保无论从哪个目录运行脚本都能找到文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(script_dir, "发球机相关文档.xlsx")
    position_file = os.path.join(script_dir, "postion.json")
    
    print(f"脚本目录: {script_dir}")
    print(f"尝试打开文件: {excel_file}")
    print(f"文件是否存在: {os.path.exists(excel_file)}")
    print(f"尝试打开站位文件: {position_file}")
    print(f"站位文件是否存在: {os.path.exists(position_file)}")
    
    try:
        # 首先查看所有sheet名称
        excel_file_obj = pd.ExcelFile(excel_file)
        print(f"Excel中的Sheet名称: {excel_file_obj.sheet_names}")
        
        # 尝试读取数据，使用第一个和第二个sheet
        legacy_df = pd.read_excel(excel_file, sheet_name=0, header=0)
        print(f"\nSheet 1 列名: {legacy_df.columns.tolist()}")
        print(f"Sheet 1 数据行数: {len(legacy_df)}")
        print(f"Sheet 1 前几行:\n{legacy_df.head()}")
        
        if len(excel_file_obj.sheet_names) > 1:
            spoball_df = pd.read_excel(excel_file, sheet_name=1, header=0)
            print(f"\nSheet 2 列名: {spoball_df.columns.tolist()}")
            print(f"Sheet 2 数据行数: {len(spoball_df)}")
            print(f"Sheet 2 前几行:\n{spoball_df.head()}")
        else:
            print("\nExcel文件中没有第二个Sheet")
            spoball_df = pd.DataFrame()
        
        print("\n" + "="*50)
        print("执行SQL生成:")
        print("="*50 + "\n")
        positioning_data = load_positioning_data(position_file)
        generate_sql_and_json(legacy_df, spoball_df, positioning_data)
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{excel_file}'")
        print("请确保Excel文件存在")
    except Exception as e:
        print(f"处理出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
