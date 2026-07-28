#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

url = "http://160.202.254.160:19581/"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    print("=" * 50)
    print("【状态码】", response.status_code)
    print("=" * 50)
    
    print("\n【响应头】")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 50)
    print("【响应正文（页面源码）】")
    # 如果内容太长，可改为 print(response.text[:500]) 并加上 "...（截断）"
    print(response.text)
    print("=" * 50)
    
    print("\n【Flag 检索结果】")
    found = False
    # 先查响应头
    for key, value in response.headers.items():
        if "flag" in key.lower() or "flag" in value.lower():
            print(f"✅ 在响应头中发现 -> {key}: {value}")
            found = True
    # 如果头里没有，再查正文（不过这道题大概率在头里）
    if not found:
        if "flag" in response.text.lower():
            print("⚠️ 响应头中未找到，但在响应正文中发现了 'flag' 关键字，请检查上面的正文输出。")
        else:
            print("❌ 未在任何地方发现 'flag' 关键字。")
    
except requests.exceptions.RequestException as e:
    print(f"❌ 请求失败: {e}")
