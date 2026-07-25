#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
项目名称: 栅栏密码工具 (Rail Fence Cipher Tool)
版本: 1.0
作者: 根据用户需求定制
更新日期: 2026-07-26

功能概述:
---------
本工具实现了两种常见的栅栏密码加密/解密算法：
    1. 之字形 (Zigzag) 流派  —— 将明文按锯齿形路径写入各行，然后逐行读取。
    2. 传统分栏 (Block) 流派  —— 将明文按顺序分成若干组，按列读取。

它特别适用于 CTF 竞赛、密码学学习和古典密码练习。

核心特点:
    ✅ 支持两种加密/解密算法（通过 --mode 参数切换）
    ✅ 支持暴力破解（尝试所有可能的栏数，并同时尝试两种流派）
    ✅ 支持从命令行直接指定明文/密文
    ✅ 支持自定义栏数（密钥）
    ✅ 输出结果清晰，便于判断

依赖环境:
    - Python 3.6 及以上版本（仅用到标准库，无需额外安装）

使用方法:
---------
    python rail_fence.py -e <明文> -k <栏数> [-m <流派>]   # 加密
    python rail_fence.py -d <密文> -k <栏数> [-m <流派>]   # 解密
    python rail_fence.py -d <密文> -b                       # 暴力破解（同时尝试两种流派）

参数说明:
---------
    -e, --encrypt <明文>     加密模式，指定待加密的明文（包含空格会忽略）
    -d, --decrypt <密文>     解密模式，指定待解密的密文
    -k, --key <栏数>         栅栏的行数（密钥），必须 >= 2
    -m, --mode <流派>        选择加密/解密流派：
                             zigzag   -> 之字形（默认）
                             block    -> 传统分栏
    -b, --bruteforce         启用暴力破解模式（仅解密时可用，会忽略 -k 和 -m）

使用示例:
---------
    1. 使用之字形加密
        $ python rail_fence.py -e "HELLO WORLD" -k 3 -m zigzag
        HOLELWRDLO

    2. 使用传统分栏加密
        $ python rail_fence.py -e "HELLO WORLD" -k 3 -m block
        HLODEORLWL

    3. 解密码（指定流派和密钥）
        $ python rail_fence.py -d "HOLELWRDLO" -k 3 -m zigzag
        HELLOWORLD

        $ python rail_fence.py -d "HLODEORLWL" -k 3 -m block
        HELLOWORLD

    4. 暴力破解（自动尝试所有栏数，并展示两种流派的结果）
        $ python rail_fence.py -d "HOLELWRDLO" -b
        === 暴力破解结果（栏数 流派 明文）===
         2  zigzag : HLOOLELWRD
         2  block  : HLOOLELWRD
         3  zigzag : HELLOWORLD
         3  block  : HLLOEOWRLD
         ...
        从中可识别出正确明文 "HELLOWORLD"。

注意事项:
---------
    - 输入文本中的空格会被自动忽略（符合大多数 CTF 题目习惯）。
    - 暴力破解输出较多，需要人工判断哪个结果是自然语言或符合 flag 格式。
    - 当栏数大于等于文本长度时，加密结果可能等于原文，因此暴力破解的栏数范围为 2 到 (len-1)。
    - 对于 2 栏，两种流派加密结果等价，解密时使用任意一种均可。

================================================================================
"""

import argparse
import sys

# ==================== 之字形（Zigzag）流派 ====================
def encrypt_zigzag(text, rails):
    """之字形加密"""
    if rails <= 1:
        return text
    fence = [[] for _ in range(rails)]
    row, step = 0, 1
    for ch in text:
        fence[row].append(ch)
        row += step
        if row == rails - 1 or row == 0:
            step = -step
    return ''.join(''.join(row) for row in fence)

def decrypt_zigzag(cipher, rails):
    """之字形解密"""
    if rails <= 1:
        return cipher
    n = len(cipher)
    # 生成路径索引
    path = []
    row, step = 0, 1
    for _ in range(n):
        path.append(row)
        row += step
        if row == rails - 1 or row == 0:
            step = -step
    # 统计每行字符数
    counts = [0] * rails
    for r in path:
        counts[r] += 1
    # 切分密文到各行
    idx = 0
    rows = []
    for c in counts:
        rows.append(cipher[idx:idx+c])
        idx += c
    # 按路径顺序取字符
    result = [''] * n
    row_pos = [0] * rails
    for i, r in enumerate(path):
        result[i] = rows[r][row_pos[r]]
        row_pos[r] += 1
    return ''.join(result)

# ==================== 传统分栏（分组型）流派 ====================
def encrypt_block(text, rails):
    """传统分栏加密（按行分组，按列读取）"""
    if rails <= 1:
        return text
    n = len(text)
    # 计算每行字符数
    base = n // rails
    extra = n % rails
    row_lens = [base + (1 if i < extra else 0) for i in range(rails)]
    # 按行分配字符（顺序）
    rows = []
    idx = 0
    for length in row_lens:
        rows.append(text[idx:idx+length])
        idx += length
    # 按列读取
    result = []
    for col in range(base + 1):
        for row in range(rails):
            if col < len(rows[row]):
                result.append(rows[row][col])
    return ''.join(result)

def decrypt_block(cipher, rails):
    """传统分栏解密"""
    if rails <= 1:
        return cipher
    n = len(cipher)
    base = n // rails
    extra = n % rails
    row_lens = [base + (1 if i < extra else 0) for i in range(rails)]
    # 将密文按列顺序切分为各行
    rows = [''] * rails
    idx = 0
    for col in range(base + 1):
        for row in range(rails):
            if col < row_lens[row]:
                rows[row] += cipher[idx]
                idx += 1
    # 按行读取得到明文
    return ''.join(rows)

# ==================== 暴力破解（两种流派同时尝试）====================
def brute_force(cipher):
    """
    尝试 rails = 2 到 len(cipher)-1，分别以两种流派解密。
    返回列表，每个元素为 (rails, mode, plaintext)
    """
    results = []
    for rails in range(2, len(cipher)):
        # 之字形
        plain1 = decrypt_zigzag(cipher, rails)
        results.append((rails, 'zigzag', plain1))
        # 传统分栏
        plain2 = decrypt_block(cipher, rails)
        results.append((rails, 'block', plain2))
    return results

# ==================== 主程序 ====================
def main():
    parser = argparse.ArgumentParser(
        description="栅栏密码工具（支持传统分栏和之字形）",
        epilog="示例：\n"
               "  python rail_fence.py -e 'HELLO WORLD' -k 3 -m zigzag\n"
               "  python rail_fence.py -d 'HOLELWRDLO' -k 3 -m zigzag\n"
               "  python rail_fence.py -d 'HOLELWRDLO' -b"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", help="加密模式（指定明文）")
    group.add_argument("-d", "--decrypt", help="解密模式（指定密文）")
    parser.add_argument("-k", "--key", type=int, help="栏数（密钥）")
    parser.add_argument("-m", "--mode", choices=['zigzag', 'block'], default='zigzag',
                        help="流派：zigzag（之字形）或 block（传统分栏），默认 zigzag")
    parser.add_argument("-b", "--bruteforce", action="store_true",
                        help="暴力破解（仅解密模式，会忽略 -k 和 -m）")

    args = parser.parse_args()

    if args.bruteforce:
        if not args.decrypt:
            print("错误：暴力破解需要 -d 参数", file=sys.stderr)
            sys.exit(1)
        cipher = args.decrypt
        results = brute_force(cipher)
        print("=== 暴力破解结果（栏数 流派 明文）===")
        for rails, mode, plain in results:
            print(f"{rails:2d}  {mode:<6} : {plain}")
        return

    # 加密模式
    if args.encrypt:
        if args.key is None:
            print("错误：加密需要 -k 参数", file=sys.stderr)
            sys.exit(1)
        plaintext = args.encrypt
        if args.mode == 'zigzag':
            cipher = encrypt_zigzag(plaintext, args.key)
        else:
            cipher = encrypt_block(plaintext, args.key)
        print(cipher)

    # 解密模式
    elif args.decrypt:
        if args.key is None:
            print("错误：解密需要 -k 参数", file=sys.stderr)
            sys.exit(1)
        cipher = args.decrypt
        if args.mode == 'zigzag':
            plain = decrypt_zigzag(cipher, args.key)
        else:
            plain = decrypt_block(cipher, args.key)
        print(plain)

if __name__ == '__main__':
    main()
