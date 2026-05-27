import pandas as pd
import json
import re
from typing import Dict, List, Any

TARGET_HAND = "右手"


def normalize_hand(hand_value: Any) -> str:
    """统一手型写法，兼容 左/右/左手/右手/不区分。"""
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


def parse_coordinates(cell_text: Any) -> dict | None:
    """解析 X：268-368\nY：219-391 格式的坐标，返回 {"x": "268-368", "y": "219-391"}"""
    if pd.isna(cell_text) or not str(cell_text).strip():
        return None

    text = str(cell_text).strip()
    x_match = re.search(r'X[：:]\s*([\d-]+)', text)
    y_match = re.search(r'Y[：:]\s*([\d-]+)', text)
    if x_match and y_match:
        return {"x": x_match.group(1), "y": y_match.group(1)}
    return None


def process_positioning_sheet(sheet_df: pd.DataFrame) -> Dict[str, List[Dict]]:
    """处理学员站位图Sheet，返回以 plan_number 为 key 的 student-positioning 映射。"""
    sheet_df = sheet_df.ffill()
    hand_priority = {TARGET_HAND: 2, "不区分": 1}
    positioning_data = {}

    pos_cols = ['站位坐标-难度（低）', '站位坐标-难度（默认）', '站位坐标-难度（高）']

    for _, row in sheet_df.iterrows():
        plan_number = row.get('编号')
        if pd.isna(plan_number):
            continue
        plan_key = str(int(plan_number))

        handedness = normalize_hand(row.get('持拍手区分'))
        if handedness not in hand_priority:
            continue

        positions = []
        for diff_level, col in enumerate(pos_cols, start=1):
            if col not in sheet_df.columns:
                continue
            coord = parse_coordinates(row[col])
            if coord:
                positions.append({"difficulty": diff_level, **coord})

        if not positions:
            continue

        current = positioning_data.get(plan_key)
        if current is None or hand_priority[handedness] > current["priority"]:
            positioning_data[plan_key] = {
                "priority": hand_priority[handedness],
                "student-positioning": positions,
            }

    return {
        pn: data["student-positioning"]
        for pn, data in positioning_data.items()
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
    """处理单个Sheet，返回以 plan_number 为 key 的参数映射。"""
    plan_data = {}

    sheet_df = sheet_df.ffill()

    for _, row in sheet_df.iterrows():
        plan_number = str(int(row['编号'])) if pd.notna(row['编号']) else None
        handedness = normalize_hand(row['持拍手区分'])

        if not plan_number or plan_number == 'nan':
            continue

        # 仅处理目标手型或"不区分"的数据
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
    positioning_df: pd.DataFrame | None = None,
):
    """主函数：生成JSON数据并输出SQL语句。"""
    # 处理普尚数据
    legacy_data = process_sheet(legacy_df, "legacy-pb")
    print(f"普尚数据处理完成，包含 {len(legacy_data)} 个plan_number")

    # 处理SBAS数据
    spoball_data = process_sheet(spoball_df, "spoball-v1")
    print(f"SBAS数据处理完成，包含 {len(spoball_data)} 个plan_number")

    # 处理学员站位数据
    if positioning_df is not None and not positioning_df.empty:
        positioning_data = process_positioning_sheet(positioning_df)
    else:
        positioning_data = {}
    print(f"学生站位数据处理完成，包含 {len(positioning_data)} 个plan_number")

    # 合并数据并生成SQL，仅处理有学员站位数据的plan_number
    all_plans = set(positioning_data.keys())
    skipped = set(legacy_data.keys()).union(set(spoball_data.keys())) - all_plans
    if skipped:
        print(f"跳过无站位数据的plan_number: {sorted(skipped)}")
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
        if TARGET_HAND == "左手":
            sql = f"UPDATE `training_plan` SET `ball_machine_left` = '{json_str}' WHERE `plan_number` = {plan_number};"
        else:
            sql = f"UPDATE `training_plan` SET `ball_machine_right` = '{json_str}' WHERE `plan_number` = {plan_number};"
        print(sql)


if __name__ == "__main__":
    import os

    # 相对于脚本文件的路径，确保无论从哪个目录运行脚本都能找到文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(script_dir, "发球机相关文档.xlsx")

    print(f"脚本目录: {script_dir}")
    print(f"尝试打开文件: {excel_file}")
    print(f"文件是否存在: {os.path.exists(excel_file)}")

    try:
        # 查看所有sheet名称
        excel_file_obj = pd.ExcelFile(excel_file)
        print(f"Excel中的Sheet名称: {excel_file_obj.sheet_names}")

        # 从指定名称的Sheet读取数据
        legacy_df = pd.read_excel(excel_file, sheet_name="普尚发球机参数", header=0)
        print(f"\n普尚发球机参数 列名: {legacy_df.columns.tolist()}")
        print(f"普尚发球机参数 数据行数: {len(legacy_df)}")

        spoball_df = pd.read_excel(excel_file, sheet_name="SBAS发球机参数", header=0)
        print(f"\nSBAS发球机参数 列名: {spoball_df.columns.tolist()}")
        print(f"SBAS发球机参数 数据行数: {len(spoball_df)}")

        positioning_df = pd.read_excel(excel_file, sheet_name="学员站位图", header=0)
        print(f"\n学员站位图 列名: {positioning_df.columns.tolist()}")
        print(f"学员站位图 数据行数: {len(positioning_df)}")

        print("\n" + "=" * 50)
        print("执行SQL生成:")
        print("=" * 50 + "\n")
        generate_sql_and_json(legacy_df, spoball_df, positioning_df)

    except FileNotFoundError:
        print(f"错误: 找不到文件 '{excel_file}'")
        print("请确保Excel文件存在")
    except ValueError as e:
        print(f"错误: Sheet名称不正确 - {e}")
        print("请检查Excel中的Sheet名称是否为: 普尚发球机参数, SBAS发球机参数, 学员站位图")
    except Exception as e:
        print(f"处理出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
