import requests

# ===================== 配置区 =====================
# 把你要验证的URL全部放这里
URL_LIST = [
    "https://files.coachai.net/courses/train/1001_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1002_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1003_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1005_student_v2-new.mp4",
"https://files.coachai.net/courses/train/1007_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1008_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1004_student_v2-new.mp4",
"https://files.coachai.net/courses/train/1006_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1009_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1010_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2003_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2006_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2009_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2015_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2016_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2017_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2019_student_v2-new.mp4",
"https://files.coachai.net/courses/train/2001_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2002_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2010_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2011_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2012_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2004_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2005_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2007_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2008_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2013_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2014_student_v1-new.mp4",
"https://files.coachai.net/courses/train/2018_student_v2-new.mp4",
"https://files.coachai.net/courses/train/3005_student_v3-new.mp4",
"https://files.coachai.net/courses/train/3007_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3019_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3020_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3003_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3009_student_v2-new.mp4",
"https://files.coachai.net/courses/train/3011_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3012_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3013_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3015_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3016_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3017_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3018_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3022_student_v2-new.mp4",
"https://files.coachai.net/courses/train/3010_student_v2-new.mp4",
"https://files.coachai.net/courses/train/3014_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3021_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3001_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3002_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3004_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3006_student_v1-new.mp4",
"https://files.coachai.net/courses/train/3008_student_v1-new.mp4",
"https://files.coachai.net/courses/train/11002_student_v2-new.mp4",
"https://files.coachai.net/courses/train/11003_student_v1-new.mp4",
"https://files.coachai.net/courses/train/21005_student_v1-new.mp4",
"https://files.coachai.net/courses/train/31001_student_v1-new.mp4",
"https://files.coachai.net/courses/train/31002_student_v1-new.mp4",
"https://files.coachai.net/courses/train/41001_student_v1-new.mp4",
"https://files.coachai.net/courses/train/course_beforce1.mp4",
"https://files.coachai.net/courses/train/course_after_v2-new.mp4",
"https://files.coachai.net/courses/train/game_v1.mp4",
"https://files.coachai.net/courses/train/1011_student_v1-new.mp4",
"https://files.coachai.net/courses/train/1011_student_v1-new.mp4",
# 往下继续加你的链接
]

# 超时时间（秒）
TIMEOUT = 15
# ===================================================

# 记录坏链接
bad_urls = []

print("===== 开始逐个验证视频URL =====")

for index, url in enumerate(URL_LIST, 1):
    print(f"\n[{index}/{len(URL_LIST)}] 检查中: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Range": "bytes=0-1024"  # 只请求一点点，适合视频
    }

    try:
        # 发送请求
        resp = requests.head(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        
        # 视频正常访问：200 / 206 都算有效
        if resp.status_code in (200, 206):
            print(f"✅ 正常访问")
        else:
            print(f"❌ 异常 状态码: {resp.status_code}")
            bad_urls.append(f"{url} | 状态码：{resp.status_code}")

    except requests.exceptions.Timeout:
        print(f"⏱️ 超时")
        bad_urls.append(f"{url} | 超时")
    
    except requests.exceptions.ConnectionError:
        print(f"🔌 无法连接")
        bad_urls.append(f"{url} | 连接失败")
    
    except Exception as e:
        print(f"⚠️ 错误: {str(e)[:50]}")
        bad_urls.append(f"{url} | 错误：{str(e)}")

# ===================== 结果输出 =====================
print("\n" + "="*50)
print(f"✅ 正常链接：{len(URL_LIST) - len(bad_urls)} 个")
print(f"❌ 异常链接：{len(bad_urls)} 个")
print("="*50)

# 保存异常链接到文件
if bad_urls:
    with open("bad_urls.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(bad_urls))
    print("\n异常URL已保存到：bad_urls.txt")

    # 打印所有异常URL
    print("\n===== 异常URL列表 =====")
    for bad in bad_urls:
        print(bad)