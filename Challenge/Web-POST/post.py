import requests

url = "http://160.202.254.160:16722/"
payload = {"what": "flag"}

# 模拟浏览器请求头(可选,但建议加上)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
    "Content-Type": "application/x-www-form-urlencoded",  # POST 表单格式
}

response = requests.post(url, data=payload, headers=headers)

# 判断是否成功拿到 flag
if "flag{" in response.text:
    print("✅ 成功获取 Flag:")
    print(response.text)
else:
    print("❌ 未找到 Flag,返回内容如下:")
    print(response.text)
