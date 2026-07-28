#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
                   进制转换器 + 文件内容进制分析 + 多编码字符串提取
================================================================================

项目名称
    HexConverter Pro

项目简介
    HexConverter Pro 是一个强大的命令行工具，提供三种核心功能：
    1. 交互式进制转换：支持 2~36 进制任意互转，并显示数值的多种进制表示，
       以及将该数值作为大端字节序列时，在多种编码（ASCII, UTF-8, UTF-16LE,
       UTF-16BE, GBK）下的可打印字符串（如果全部可打印）。
    2. 文件整体进制分析：将任意文件的所有字节视为一个大整数，
       输出其十进制、二进制、八进制、十六进制表示。
    3. 多编码可打印字符串提取：扫描文件，尝试多种编码解码，提取所有连续
       的可打印字符序列（长度≥4），并显示对应的十六进制字节串。

应用场景
    • CTF 竞赛中快速分析二进制文件，提取隐藏的 flag。
    • 日常开发中查看二进制文件的明文片段。
    • 对十六进制或编码字符串进行快速转换和验证。
    • 在交互模式下，探索数值的字节表示及可打印字符串。

核心功能
    🔢 进制转换（交互模式）
        - 支持 2~36 进制任意互转。
        - 转换后显示十进制、二进制、八进制、十六进制。
        - 将数值转为大端字节序列，显示其十六进制字节串。
        - 用多种编码解码该字节序列，若结果全部为可打印字符，则显示该字符串。

    📁 文件整体进制分析（文件模式）
        - 读取整个文件，解释为大端序整数。
        - 输出十进制、二进制、八进制、十六进制（按字节分组）。
        - 提取 ASCII 及多编码可打印字符串（长度≥4）并显示十六进制。

    🔍 多编码可打印字符串提取（文件模式）
        - 支持的编码：ASCII、UTF-8、UTF-16LE、UTF-16BE、GBK。
        - 对每个编码，解码整个文件（替换无效字节），找出连续的可打印字符片段。
        - 输出每个片段的文本内容及对应的原始字节十六进制串。

安装与依赖
    无需安装第三方库，仅需 Python 3.6 及以上版本（使用标准库）。

使用方法
    1. 交互模式（无参数）：
           python converter.py
       按提示输入数字、源进制、目标进制。

    2. 文件分析模式：
           python converter.py -f <文件路径>
       将分析指定文件并输出进制信息和提取的字符串。

命令行参数
    -f, --file <path>    指定要分析的文件（启用文件模式）
    -h, --help           显示帮助信息

使用案例
    见文档末尾。

版本历史
    v5.2 (2026-07-28) - 删除 UTF-32 编码支持，精简编码列表
    v5.1 (2026-07-28) - 交互模式增加多编码字节序列可打印字符串显示
    v5.0 (2026-07-28) - 新增多编码可打印字符串提取（UTF-8, UTF-16LE/BE, GBK）
    v4.0 (2026-07-26) - 增加文件整体进制分析及 ASCII strings
    v1.0 (初始版本)   - 交互式进制转换

作者
    CTF-Tools 团队
许可证
    MIT License
================================================================================
"""

import argparse
import sys
import os


# ---------- 核心功能：进制转换 ----------

def from_base10(num: int, base: int) -> str:
    if num == 0:
        return "0"
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    while num > 0:
        remainder = num % base
        result = digits[remainder] + result
        num //= base
    return result


def convert(num_str: str, from_base: int, to_base: int) -> str:
    try:
        decimal_value = int(num_str, from_base)
    except ValueError:
        raise ValueError(f"无效数字 '{num_str}' 对于进制 {from_base}")
    return from_base10(decimal_value, to_base)


# ---------- 字节序列多编码可打印字符串检测（交互模式用） ----------

def display_byte_encodings(value: int) -> None:
    """
    将整数转换为大端字节序列，尝试多种编码解码整个字节序列，
    若解码后全部为可打印字符（不含替换字符），则显示该字符串及其十六进制。
    """
    if value == 0:
        byte_data = b'\x00'
    else:
        byte_length = (value.bit_length() + 7) // 8
        byte_data = value.to_bytes(byte_length, 'big')

    print(f"字节十六进制: {' '.join(f'{b:02X}' for b in byte_data)}")

    # 定义编码列表（已移除 UTF-32）
    encodings = [
        ('ASCII', 'ascii'),
        ('UTF-8', 'utf-8'),
        ('UTF-16LE', 'utf-16-le'),
        ('UTF-16BE', 'utf-16-be'),
        ('GBK', 'gbk'),
    ]

    found_any = False
    for name, enc in encodings:
        try:
            decoded = byte_data.decode(enc, errors='replace')
        except (LookupError, UnicodeDecodeError):
            continue
        # 检查是否包含替换字符，且所有字符可打印
        if '\ufffd' in decoded:
            continue
        if all(ch.isprintable() for ch in decoded):
            print(f"{name} 可打印字符串: \"{decoded}\"")
            found_any = True
    if not found_any:
        print("（无编码能完全解码为可打印字符）")


# ---------- 文件模式：多编码可打印字符串提取 ----------

def extract_strings_by_encoding(data: bytes, encoding: str, min_len: int = 4):
    """
    尝试用指定编码解码整个字节串（errors='replace'），
    找出其中连续的可打印字符片段（长度>=min_len），
    返回列表，每个元素为 (解码后的文本片段, 对应原始字节的十六进制字符串)。
    """
    try:
        decoded = data.decode(encoding, errors='replace')
    except (LookupError, UnicodeDecodeError):
        return []

    results = []
    i = 0
    n = len(decoded)
    while i < n:
        # 寻找可打印字符且不是替换字符
        if decoded[i].isprintable() and decoded[i] != '\ufffd':
            start = i
            while i < n and decoded[i].isprintable() and decoded[i] != '\ufffd':
                i += 1
            end = i
            text = decoded[start:end]
            if len(text) >= min_len:
                raw_bytes = data[start:end]  # 解码后长度等于原始长度（因为 errors='replace'）
                hex_repr = ' '.join(f'{b:02X}' for b in raw_bytes)
                results.append((text, hex_repr))
        else:
            i += 1
    return results


# ---------- 文件分析 ----------

def analyze_file(filepath: str) -> None:
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"错误: 文件 '{filepath}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"读取文件出错: {e}")
        sys.exit(1)

    size = len(data)
    print("=" * 50)
    print(f"文件分析: {filepath}")
    print(f"文件大小: {size} 字节")
    print("=" * 50)

    if size == 0:
        print("文件为空。")
        return

    # 整体进制表示
    integer = int.from_bytes(data, 'big')
    print("\n十进制整数:")
    print(integer)
    print("\n二进制表示:")
    print(format(integer, 'b'))
    print("\n八进制表示:")
    print(format(integer, 'o'))
    print("\n十六进制表示:")
    hex_str = format(integer, 'X')
    if len(hex_str) % 2 == 1:
        hex_str = '0' + hex_str
    grouped_hex = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
    print(grouped_hex)

    # 提取 ASCII 字符串（经典 strings）
    print("\n" + "=" * 50)
    print("ASCII 可打印字符串 (长度≥4) 及其十六进制:")
    ascii_strings = extract_strings_by_encoding(data, 'ascii', min_len=4)
    if ascii_strings:
        for text, hex_repr in ascii_strings:
            print(f"  {text}")
            print(f"    hex: {hex_repr}")
    else:
        print("  (未找到)")

    # 多编码尝试（已移除 UTF-32）
    encodings = [
        ('UTF-8', 'utf-8'),
        ('UTF-16LE', 'utf-16-le'),
        ('UTF-16BE', 'utf-16-be'),
        ('GBK', 'gbk'),
    ]
    for name, enc in encodings:
        print("\n" + "=" * 50)
        print(f"{name} 可打印字符串 (长度≥4) 及其十六进制:")
        strings = extract_strings_by_encoding(data, enc, min_len=4)
        if strings:
            for text, hex_repr in strings:
                print(f"  {text}")
                print(f"    hex: {hex_repr}")
        else:
            print("  (未找到)")


# ---------- 交互模式 ----------

def interactive_mode():
    print("=" * 55)
    print("         进制转换器 + 字节序列多编码可打印字符串")
    print("=" * 55)
    print("说明：")
    print("  • 数字 0~9，字母 A~Z 表示 10~35（不区分大小写）")
    print("  • 转换后自动显示数值的进制信息，以及该数值的大端字节序列")
    print("  • 尝试用 ASCII, UTF-8, UTF-16LE, UTF-16BE, GBK 解码字节序列")
    print("  • 若解码后全部为可打印字符，则显示对应字符串")
    print("  • 输入 'q' 退出程序\n")

    while True:
        try:
            num = input("请输入要转换的数字 (或 'q' 退出): ").strip()
            if num.lower() == 'q':
                break
            from_base = int(input("请输入源进制 (2-36): "))
            to_base = int(input("请输入目标进制 (2-36): "))
            if not (2 <= from_base <= 36) or not (2 <= to_base <= 36):
                print("错误：进制必须在 2 到 36 之间\n")
                continue
            decimal_value = int(num, from_base)

            print("\n--- 数值详细信息 ---")
            print(f"十进制  : {decimal_value}")
            print(f"二进制  : {format(decimal_value, 'b')}")
            print(f"八进制  : {format(decimal_value, 'o')}")
            print(f"十六进制: {format(decimal_value, 'X')}")

            # 显示字节序列多编码解析
            display_byte_encodings(decimal_value)

            result = convert(num, from_base, to_base)
            print(f"\n转换结果（{from_base}进制 → {to_base}进制）: {result}\n")
        except ValueError as e:
            print(f"输入错误: {e}\n")
        except KeyboardInterrupt:
            print("\n程序已退出")
            break
        except Exception as e:
            print(f"未知错误: {e}\n")


# ---------- 主程序 ----------

def main():
    parser = argparse.ArgumentParser(
        description="进制转换器 + 文件内容进制分析 + 多编码可打印字符串提取",
        epilog="使用 -f 分析文件，无参数则进入交互模式。"
    )
    parser.add_argument("-f", "--file", help="指定要分析的文件路径")
    args = parser.parse_args()

    if args.file:
        analyze_file(args.file)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
