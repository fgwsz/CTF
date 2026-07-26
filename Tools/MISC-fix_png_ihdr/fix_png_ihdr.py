#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PNG IHDR CRC 爆破修复工具
----------------------------
功能：当PNG图片的IHDR块宽高被修改但CRC未更新时，通过暴力枚举宽高组合，
      匹配原始CRC值，从而恢复正确的图片尺寸并修复文件。

用法：
    python fix_png_ihdr.py <输入文件> [输出文件]

如果不指定输出文件，则自动在当前目录生成 fixed_<原文件名>.png。
如果输出路径包含不存在的目录，会自动创建。

示例：
    python fix_png_ihdr.py broken.png
    python fix_png_ihdr.py broken.png repaired.png
    python fix_png_ihdr.py ./images/broken.png ./output/fixed.png
"""

import struct
import zlib
import sys
import os

def get_ihdr_data(png_bytes):
    """解析PNG，返回IHDR块的数据部分（13字节）和存储的CRC"""
    if png_bytes[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("不是有效的PNG文件")
    
    pos = 8  # 跳过文件签名
    while pos + 8 <= len(png_bytes):
        length = struct.unpack('>I', png_bytes[pos:pos+4])[0]
        chunk_type = png_bytes[pos+4:pos+8]
        if chunk_type == b'IHDR':
            data_start = pos + 8
            data = png_bytes[data_start:data_start+length]
            crc_start = data_start + length
            stored_crc = struct.unpack('>I', png_bytes[crc_start:crc_start+4])[0]
            if length != 13:
                raise ValueError("IHDR数据长度不是13，可能损坏")
            return data, stored_crc, data_start, crc_start
        pos += 4 + 4 + length + 4
    raise ValueError("未找到IHDR块")

def brute_force_crc(ihdr_data, stored_crc, max_wh=4000, verbose=True):
    """
    爆破宽度和高度，返回匹配的宽高以及新的IHDR数据。
    如果verbose为True，每1000次打印一次状态。
    """
    fixed = ihdr_data[8:13]  # 位深、颜色、压缩、滤波、隔行
    if verbose:
        print(f"[*] 固定字节: {fixed.hex()}")
        print(f"[*] 存储的CRC: {hex(stored_crc)}")
        print(f"[*] 开始爆破宽高（1~{max_wh}）...")
    
    total = max_wh * max_wh
    count = 0
    for w in range(1, max_wh+1):
        for h in range(1, max_wh+1):
            test_data = struct.pack('>II', w, h) + fixed
            crc = zlib.crc32(b'IHDR' + test_data) & 0xffffffff
            count += 1
            if verbose and count % 1000 == 0:
                print(f"[*] 已尝试 {count}/{total} 组合...")
            if crc == stored_crc:
                return w, h, test_data
    return None, None, None

def fix_png(input_path, output_path=None):
    if output_path is None:
        # 默认输出到当前目录
        base = os.path.basename(input_path)
        name, ext = os.path.splitext(base)
        output_path = f"fixed_{name}{ext}"
    else:
        # 确保输出目录存在
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"[-] 文件 {input_path} 不存在")
        return
    except Exception as e:
        print(f"[-] 读取文件失败: {e}")
        return

    try:
        ihdr_data, stored_crc, data_start, crc_start = get_ihdr_data(data)
    except Exception as e:
        print(f"[-] 解析PNG失败: {e}")
        return

    orig_w, orig_h = struct.unpack('>II', ihdr_data[:8])
    print(f"[*] 文件中的宽高: {orig_w} x {orig_h}")
    
    # 爆破
    w, h, new_data = brute_force_crc(ihdr_data, stored_crc, max_wh=4000, verbose=True)
    if w is None:
        print("[-] 未找到匹配的宽高，请扩大范围或检查文件是否损坏。")
        return

    print(f"[+] 找到匹配! 宽度: {w}, 高度: {h}")
    print(f"[+] 新IHDR数据: {new_data.hex()}")

    # 构造修复后的PNG
    new_crc = zlib.crc32(b'IHDR' + new_data) & 0xffffffff
    new_crc_bytes = struct.pack('>I', new_crc)
    # 替换IHDR数据和CRC
    new_file = data[:data_start] + new_data + new_crc_bytes + data[crc_start+4:]

    try:
        with open(output_path, 'wb') as f:
            f.write(new_file)
        print(f"[+] 修复完成，保存为: {output_path}")
    except Exception as e:
        print(f"[-] 写入文件失败: {e}")

def main():
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <输入文件> [输出文件]")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    fix_png(input_file, output_file)

if __name__ == "__main__":
    main()
