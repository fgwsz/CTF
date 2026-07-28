#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os

def decode_key_exe():
    input_file = "export/KEY.exe"
    output_file = "image.jpg"

    # 检查输入文件是否存在
    if not os.path.isfile(input_file):
        print(f"错误：找不到文件 {input_file}")
        return

    # 读取文件内容（文本模式）
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # 查找 base64 数据起始位置
    # 格式为 "data:image/jpg;base64,<base64_data>"
    prefix = "data:image/jpg;base64,"
    if content.startswith(prefix):
        b64_data = content[len(prefix):]
    else:
        # 兼容没有前缀的情况，直接当作纯 Base64
        b64_data = content

    # 解码 Base64
    try:
        img_data = base64.b64decode(b64_data)
    except Exception as e:
        print(f"Base64 解码失败: {e}")
        return

    # 写入二进制文件
    with open(output_file, "wb") as f:
        f.write(img_data)

    print(f"成功！图片已保存为 {output_file}")

if __name__ == "__main__":
    decode_key_exe()
