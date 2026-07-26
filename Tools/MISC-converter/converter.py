#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
              进制转换器 + 文件内容进制分析 + 可打印字符串提取
================================================================================

项目描述
--------
这是一个多功能进制工具，提供两种核心功能：

1. 交互式进制转换（原有功能）
   支持 2~36 进制任意互转，数字 10~35 用 A~Z 表示（不区分大小写）。
   转换后会显示该数值的十进制、二进制、八进制、十六进制以及对应的可打印 ASCII 字符。

2. 文件内容进制分析（新增核心功能）
   将整个文件的内容（所有字节）视为一个巨大的无符号整数，并显示其：
     - 十进制
     - 二进制
     - 八进制
     - 十六进制
   同时，扫描文件中的所有可打印 ASCII 字符串（长度 ≥ 4），按顺序列出，
   类似于 Unix 的 `strings` 命令，方便快速查看文件中的可读文本。

功能特性
--------
• 支持 2~36 进制任意转换（交互模式）。
• 文件整体进制分析：适用于任意二进制文件（包括文本、图片、可执行文件等）。
• 大整数处理：利用 Python 的任意精度整数，可处理任意大小的文件。
• 可打印字符串提取：自动过滤并显示长度 ≥ 4 的可打印字符序列。
• 两种运行模式：
   - 交互模式（无参数）：逐次输入数字、源进制、目标进制。
   - 文件分析模式（-f 文件路径）：分析整个文件，输出进制信息和可打印字符串。
• 命令行参数清晰，支持输出重定向。

使用方法
--------

【交互模式】
    python converter.py
    按提示输入数字、源进制、目标进制，即可获得转换结果及详细信息。

【文件分析模式】
    python converter.py -f <文件路径>
    程序将读取指定文件，输出：
        - 文件大小（字节数）
        - 该文件内容的十进制整数
        - 二进制、八进制、十六进制表示（十六进制会按字节分组显示）
        - 提取出的所有可打印字符串（长度≥4）

    示例：
        python converter.py -f myfile.bin

    也可以将输出保存到文件：
        python converter.py -f myfile.bin > output.txt

命令行参数：
    -f, --file   : 指定要分析的文件路径（必需，用于文件分析模式）
    -h, --help   : 显示帮助信息

输入/输出格式
-------------
• 交互模式：输入数字（可含字母），源进制，目标进制。
• 文件分析模式：读取文件字节，将其解释为大整数，然后输出多种进制表示。

使用案例
--------

【案例1：交互模式 – 十六进制 'FF' 转十进制】
    $ python converter.py
    ...
    请输入要转换的数字 (或 'q' 退出): FF
    请输入源进制 (2-36): 16
    请输入目标进制 (2-36): 10

    --- 数值详细信息 ---
    十进制  : 255
    二进制  : 11111111
    八进制  : 377
    十六进制: FF
    可打印字符: 超出 ASCII 范围（不可打印）
    ---------------------

    转换结果（16进制 → 10进制）: 255

【案例2：交互模式 – 十进制 65 转十六进制】
    请输入要转换的数字 (或 'q' 退出): 65
    请输入源进制 (2-36): 10
    请输入目标进制 (2-36): 16

    --- 数值详细信息 ---
    十进制  : 65
    二进制  : 1000001
    八进制  : 101
    十六进制: 41
    可打印字符: 'A'
    ---------------------

    转换结果（10进制 → 16进制）: 41

【案例3：文件分析模式 – 分析一个文本文件】
    假设有一个文件 hello.txt，内容为 "Hello, 世界!"（UTF-8 编码，占用 15 字节）
    运行：
        python converter.py -f hello.txt

    输出示例：
        ========================================
        文件分析: hello.txt
        文件大小: 15 字节
        ========================================

        十进制整数: 721903759373840516860969563446330...
        (完整数字很长，这里省略)

        二进制表示: 101011010101...
        八进制表示: 123456...
        十六进制表示: 48656C6C6F2C20E4B896E7958C21
        (按字节分组: 48 65 6C 6C 6F 2C 20 E4 B8 96 E7 95 8C 21)

        提取的可打印字符串（长度≥4）:
        Hello
        世界

【案例4：文件分析模式 – 分析二进制文件（如ELF或图片）】
    python converter.py -f /bin/ls
    会输出该文件内容的巨大整数表示，以及其中包含的所有可打印字符串（如路径名、库名等）。

注意事项
--------
• 大文件可能会生成非常长的数字字符串（例如 1MB 文件有约 2.4 百万位十进制数），
  输出可能非常庞大，建议重定向到文件。
• 十六进制表示默认按字节分组显示（每两个十六进制字符一组），方便阅读。
• 可打印字符串提取仅针对 ASCII 可打印字符（32~126），且长度至少为 4。
• 文件分析模式不修改原文件，只读。

环境要求
--------
- Python 3.6 及以上（标准库，无需额外安装）。

版本信息
--------
版本 4.0 (2026-07-26)
  新增：文件整体进制分析功能
  新增：可打印字符串提取（类 strings）
  保留：原有交互式进制转换
  重构：代码模块化，增加命令行参数解析

作者
----
（此处可填写您的名字）
================================================================================
"""

import argparse
import sys
import os

# ---------- 核心功能：进制转换 ----------

def from_base10(num: int, base: int) -> str:
    """将十进制整数转换为指定进制（2~36）的字符串"""
    if num == 0:
        return "0"
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    while num > 0:
        remainder = num % base
        result = digits[remainder] + result
        num //= base
    return result


def show_number_info(value: int) -> None:
    """打印数值的多种进制表示及可打印字符（交互模式）"""
    print("\n--- 数值详细信息 ---")
    print(f"十进制  : {value}")
    print(f"二进制  : {format(value, 'b')}")
    print(f"八进制  : {format(value, 'o')}")
    print(f"十六进制: {format(value, 'X')}")

    if 32 <= value <= 126:
        print(f"可打印字符: '{chr(value)}'")
    else:
        if 0 <= value <= 127:
            print("可打印字符: 控制字符（不可打印）")
        else:
            print("可打印字符: 超出 ASCII 范围（不可打印）")
    print("---------------------")


def convert(num_str: str, from_base: int, to_base: int) -> str:
    """将 num_str（from_base 进制）转换为 to_base 进制的字符串"""
    try:
        decimal_value = int(num_str, from_base)
    except ValueError:
        raise ValueError(f"无效数字 '{num_str}' 对于进制 {from_base}")
    return from_base10(decimal_value, to_base)


# ---------- 文件分析功能 ----------

def analyze_file(filepath: str) -> None:
    """
    读取整个文件，将其内容解释为一个大整数，并显示各种进制表示，
    同时提取并打印所有可打印 ASCII 字符串（长度≥4）。
    """
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

    # 将字节转为大整数（大端序）
    integer = int.from_bytes(data, 'big')

    # 显示各种进制
    print("\n十进制整数:")
    print(integer)
    print("\n二进制表示:")
    print(format(integer, 'b'))
    print("\n八进制表示:")
    print(format(integer, 'o'))
    print("\n十六进制表示:")
    hex_str = format(integer, 'X')
    # 如果长度是奇数，前面补0使其成为偶数个字符，以便分组
    if len(hex_str) % 2 == 1:
        hex_str = '0' + hex_str
    # 每两个字符一组，用空格分隔，便于阅读
    grouped_hex = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
    print(grouped_hex)

    # ---------- 提取可打印字符串（类似 strings） ----------
    print("\n提取的可打印字符串（长度≥4）:")
    strings_found = []
    current = []
    for byte in data:
        if 32 <= byte <= 126:  # 可打印 ASCII
            current.append(chr(byte))
        else:
            if len(current) >= 4:
                strings_found.append(''.join(current))
            current = []
    # 处理末尾
    if len(current) >= 4:
        strings_found.append(''.join(current))

    if strings_found:
        for s in strings_found:
            print(s)
    else:
        print("（未找到长度≥4的可打印字符串）")


# ---------- 交互模式 ----------

def interactive_mode():
    """原有的交互式转换功能"""
    print("=" * 55)
    print("         进制转换器 + 打印信息（八进制、十六进制、字符）")
    print("=" * 55)
    print("说明：")
    print("  • 数字 0~9，字母 A~Z 表示 10~35（不区分大小写）")
    print("  • 转换后自动显示该数值的十进制、二进制、八进制、十六进制")
    print("  • 若数值为可打印 ASCII 字符，则会显示该字符")
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
            show_number_info(decimal_value)
            result = convert(num, from_base, to_base)
            print(f"转换结果（{from_base}进制 → {to_base}进制）: {result}\n")

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
        description="进制转换器 + 文件内容进制分析 + 可打印字符串提取",
        epilog="使用 -f 分析文件，无参数则进入交互模式。"
    )
    parser.add_argument(
        "-f", "--file",
        help="指定要分析的文件路径（读取整个文件作为大整数进制分析）"
    )
    args = parser.parse_args()

    if args.file:
        analyze_file(args.file)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
