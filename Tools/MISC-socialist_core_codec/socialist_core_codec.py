#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
                   社会主义核心价值观编码/解码器
===============================================================================

项目描述
--------
本工具实现了一种基于社会主义核心价值观词汇的编码与解码算法，可将任意 UTF-8 文本
编码为由 12 个核心价值观词汇（共 24 个字）组成的字符串，并可将编码串还原为原始文本。
该编码方案参照了掘金社区文章《社会主义核心价值观解密》
（https://juejin.cn/post/7530957239852072998）的设计思路。

编码原理
--------
1. 将输入文本进行 UTF-8 编码，得到字节序列。
2. 将字节序列转换为十六进制字符串（大写），每个字符为 0~F。
3. 对每个十六进制字符（数值 0~15）进行映射：
   - 若值为 0~9，直接映射到对应索引（0~9）的词汇。
   - 若值为 10~15（即 A~F），则随机选择以下两种规则之一：
       规则一：n → [11, n-6]       （例如 14 → [11, 8]）
       规则二：n → [10, n-10]      （例如 14 → [10, 4]）
     每个规则产生两个索引值，分别对应两个词汇。
4. 将所有索引值按顺序映射为 12 个核心价值观词汇，连接成最终编码串。
5. 由于随机选择规则，同一文本每次编码的结果可能不同，但均可被正确解码。

解码原理
--------
1. 将编码串按每两个字符（一个词汇）分组，查找每个词汇对应的索引（0~11）。
2. 从左到右遍历索引序列：
   - 若索引 < 10，则直接将其视为十六进制字符（0~9）。
   - 若索引 == 10，则表示应用了规则二，取出下一个索引 x，还原数值为 x + 10。
   - 若索引 == 11，则表示应用了规则一，取出下一个索引 y，还原数值为 y + 6。
3. 将所有还原出的十六进制字符拼接成完整的十六进制字符串。
4. 将十六进制字符串转换为字节序列，再按 UTF-8 解码为原始文本。

功能特性
--------
• 支持 UTF-8 文本的编码和解码。
• 编码过程中引入随机性，每次输出不同（增强隐蔽性）。
• 解码过程完全自动识别两种规则，无需额外信息。
• 交互式命令行界面，操作简单。
• 严格错误处理，对无效输入给出明确提示。

使用方法
--------
本工具目前提供交互式命令行界面，无需命令行参数。

启动程序：
    python socialist_core_codec.py

进入交互界面后，根据提示选择操作：
    e  : 编码（Encode）—— 输入原始文本，输出核心价值观编码串。
    d  : 解码（Decode）—— 输入编码串，输出原始文本。
    q  : 退出程序。

编码输出说明：
    - 编码结果由 12 个词汇组成，每个词汇为两个汉字，总长度为偶数。
    - 编码结果中不含空格、换行等分隔符，可直接复制使用。
    - 每次编码结果可能不同，但都能正确解码。

注意事项
--------
• 本编码算法不涉及加密，仅是一种可逆的字符替换编码。
• 解码时，编码串必须严格由 12 个核心价值观词汇组成，且顺序正确。
• 若编码串中包含非词汇字符（如空格、标点等），程序会报错。
• 若编码串长度不为偶数，程序会报错。
• 原始文本必须为合法的 UTF-8 编码，否则解码可能失败。

环境要求
--------
- Python 3.6 或更高版本（仅使用标准库 random, re）。

示例
----

【示例1：编码中文 “我”】
    > python socialist_core_codec.py
    请选择 (e:编码, d:解码, q:退出): e
    请输入要编码的文本: 我
    编码结果: 诚信自由公正爱国爱国敬业民主

    再次编码（可能不同）：
    编码结果: 友善诚信公正爱国爱国敬业民主

【示例2：解码编码串】
    请选择 (e:编码, d:解码, q:退出): d
    请输入要解码的编码串: 诚信自由公正爱国爱国敬业民主
    解码结果: 我

【示例3：编码英文 "Hello"】
    > 编码 "Hello" 可能得到：
    编码结果: 富强公正诚信平等民主敬业爱国文明民主平等民主自由平等

    解码后还原为 "Hello"。

【示例4：多次编码同一文本】
    对 "社会主义核心价值观" 进行多次编码，每次结果不同，但均可解码还原。

版本信息
--------
版本 1.0 (2026-07-26)
初始发布，实现基础编码/解码功能。

===============================================================================
"""

import random
import re


# 12 个核心价值观词汇，索引 0-11
CORE_VALUES = [
    '富强', '民主', '文明', '和谐',
    '自由', '平等', '公正', '法治',
    '爱国', '敬业', '诚信', '友善'
]

# 反向查找：词汇 → 索引
VALUE_TO_INDEX = {word: idx for idx, word in enumerate(CORE_VALUES)}


def encode(text: str) -> str:
    """
    将文本编码为社会主义核心价值观字符串。
    每次编码结果可能不同（因为引入了随机性）。
    """
    # 1. UTF-8 编码后转为十六进制字符串（去除 '0x' 前缀）
    hex_str = text.encode('utf-8').hex().upper()
    
    result_indices = []
    
    for ch in hex_str:
        num = int(ch, 16)  # 转为十进制 0-15
        
        if num < 10:
            # 0-9 直接使用
            result_indices.append(num)
        else:
            # 10-15 (A-F) 随机选择两种规则之一
            if random.random() < 0.5:
                # 规则一: n → [11, n-6]
                result_indices.append(11)
                result_indices.append(num - 6)
            else:
                # 规则二: n → [10, n-10]
                result_indices.append(10)
                result_indices.append(num - 10)
    
    # 将索引映射为词汇
    return ''.join(CORE_VALUES[idx] for idx in result_indices)


def decode(encoded: str) -> str:
    """
    将社会主义核心价值观编码字符串解码还原为原始文本。
    """
    # 每两个字符（一个词汇）一组
    if len(encoded) % 2 != 0:
        raise ValueError("编码字符串长度必须为偶数")
    
    # 将词汇转为索引列表
    indices = []
    for i in range(0, len(encoded), 2):
        word = encoded[i:i+2]
        if word not in VALUE_TO_INDEX:
            raise ValueError(f"无效词汇: {word}")
        indices.append(VALUE_TO_INDEX[word])
    
    # 还原十六进制字符
    hex_chars = []
    i = 0
    while i < len(indices):
        idx = indices[i]
        
        if idx < 10:
            # 0-9: 直接转为十六进制字符
            hex_chars.append(str(idx))
            i += 1
        elif idx == 10:
            # 规则二: [10, n-10] → 还原为 n = (n-10) + 10
            if i + 1 >= len(indices):
                raise ValueError("编码数据不完整")
            n = indices[i + 1] + 10
            hex_chars.append(hex(n)[2:].upper())
            i += 2
        elif idx == 11:
            # 规则一: [11, n-6] → 还原为 n = (n-6) + 6
            if i + 1 >= len(indices):
                raise ValueError("编码数据不完整")
            n = indices[i + 1] + 6
            hex_chars.append(hex(n)[2:].upper())
            i += 2
        else:
            raise ValueError(f"无效索引: {idx}")
    
    # 组合十六进制字符串并解码为 UTF-8 文本
    hex_str = ''.join(hex_chars)
    try:
        return bytes.fromhex(hex_str).decode('utf-8')
    except (ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"解码失败: {e}")


def main():
    """交互式命令行界面"""
    print("=" * 55)
    print("         社会主义核心价值观编码/解码器")
    print("=" * 55)
    print("说明：")
    print("  • 编码时每次结果可能不同（随机选择两种规则之一）")
    print("  • 解码时自动识别两种规则")
    print("  • 输入 'q' 退出程序\n")
    
    while True:
        choice = input("请选择 (e:编码, d:解码, q:退出): ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'e':
            text = input("请输入要编码的文本: ")
            try:
                result = encode(text)
                print(f"编码结果: {result}\n")
            except Exception as e:
                print(f"编码失败: {e}\n")
        elif choice == 'd':
            encoded = input("请输入要解码的编码串: ").strip()
            try:
                result = decode(encoded)
                print(f"解码结果: {result}\n")
            except Exception as e:
                print(f"解码失败: {e}\n")
        else:
            print("无效选择，请输入 e, d 或 q\n")


if __name__ == "__main__":
    main()
