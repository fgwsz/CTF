#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
                    Ook! / Brainfuck 解释器
===============================================================================

项目描述
--------
本工具是一个多功能的解释器，能够直接执行 Brainfuck 语言编写的程序，
同时也支持 **Ook! 语言**——一种基于 Brainfuck 的深奥编程语言，
使用 "Ook."、"Ook?" 和 "Ook!" 及其组合构成指令。

该解释器自动检测输入内容的类型：
    - 如果输入中包含 "Ook" 字样，则视为 Ook! 代码，自动转换为 Brainfuck 后执行。
    - 否则，视为 Brainfuck 代码直接执行。

适用于 CTF 竞赛中常见的 Ook! 编码题目，可快速解码并输出结果。

工作原理
--------
Brainfuck 是一种极简的图灵完备语言，由 8 个指令组成：
    >  指针右移
    <  指针左移
    +  当前单元格值加 1
    -  当前单元格值减 1
    .  输出当前单元格的 ASCII 字符
    ,  从输入读取一个字节（本解释器忽略输入）
    [  如果当前单元格值为 0，跳转到匹配的 ] 之后
    ]  如果当前单元格值不为 0，跳转到匹配的 [ 之前

Ook! 将上述 8 个指令映射为 8 个由 "Ook" 和标点符号组成的短语：
    Ook. Ook?   →  >
    Ook? Ook.   →  <
    Ook. Ook.   →  +
    Ook! Ook!   →  -
    Ook! Ook.   →  .
    Ook. Ook!   →  ,
    Ook! Ook?   →  [
    Ook? Ook!   →  ]

本解释器读取输入后，先进行词法分析，将连续的 "Ook" 单词提取出来，
每两个单词组成一个指令并映射为 Brainfuck 符号，最终执行。

使用方法
--------
命令格式：
    python ook_bf_interpreter.py [-i <输入文件>]

若不指定 -i，则从标准输入 (stdin) 读取程序。

示例
----

【示例1】直接运行 Ook! 代码文件
    $ python ook_bf_interpreter.py -i file.txt
    （输出程序执行结果，例如 flag{...}）

【示例2】通过管道传入 Ook! 代码
    $ cat file.txt | python ook_bf_interpreter.py

【示例3】直接运行 Brainfuck 代码（也会被自动识别）
    $ echo "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------." | python ook_bf_interpreter.py
    （输出 "Hello World!"）

【示例4】在交互式环境测试
    $ python ook_bf_interpreter.py
    然后粘贴代码，按 Ctrl+D (Linux) 或 Ctrl+Z (Windows) 结束输入，即可看到结果。

注意事项
--------
- 解释器使用 30000 个字节的内存单元（标准 Brainfuck 大小）。
- 输入指令中的 `,`（读取输入）被忽略，默认输入值为 0，这在大多数 CTF 题中足够。
- 代码中的空格、换行、制表符等空白字符会被忽略。
- 对于 Ook!，只有 "Ook."、"Ook?"、"Ook!" 这些 token 会被识别，其他字符会被忽略。
- 若代码中包含不完整的 token（如孤立的 "Ook"），解释器会报错提示。

依赖环境
--------
- Python 3.6 及以上（仅使用标准库）。

版本信息
--------
版本 1.0 (2026-07-27)
初始发布。

作者
----
（可填写您的名字）
===============================================================================
"""

import sys
import re
import argparse

# ---------- Ook! → Brainfuck 映射表 ----------
OOK_TO_BF = {
    "Ook. Ook?": ">",
    "Ook? Ook.": "<",
    "Ook. Ook.": "+",
    "Ook! Ook!": "-",
    "Ook! Ook.": ".",
    "Ook. Ook!": ",",
    "Ook! Ook?": "[",
    "Ook? Ook!": "]"
}

def parse_ook(text: str) -> str:
    """
    将 Ook! 代码转换为 Brainfuck 代码。
    提取所有 "Ook."、"Ook?"、"Ook!" 形式的 token，
    每两个 token 构成一个指令，映射为 BF 符号。
    """
    # 用正则匹配所有 Ook 词汇（包括标点）
    tokens = re.findall(r'Ook[.?!]', text)
    if len(tokens) % 2 != 0:
        raise ValueError("Ook! 代码的 token 数量必须是偶数（每个指令两个 token）")

    bf_chars = []
    for i in range(0, len(tokens), 2):
        pair = tokens[i] + ' ' + tokens[i+1]
        if pair not in OOK_TO_BF:
            raise ValueError(f"未知的 Ook! 指令: {pair}")
        bf_chars.append(OOK_TO_BF[pair])
    return ''.join(bf_chars)


def run_bf(code: str) -> str:
    """
    执行 Brainfuck 代码，返回输出字符串。
    内存：30000 字节，指针初始为 0。
    输入指令 ',' 被忽略（输入视为 0）。
    """
    tape = [0] * 30000
    ptr = 0
    output = []
    i = 0
    n = len(code)

    while i < n:
        c = code[i]
        if c == '>':
            ptr += 1
            if ptr >= len(tape):
                raise RuntimeError("指针超出内存范围")
        elif c == '<':
            ptr -= 1
            if ptr < 0:
                raise RuntimeError("指针超出内存范围")
        elif c == '+':
            tape[ptr] = (tape[ptr] + 1) % 256
        elif c == '-':
            tape[ptr] = (tape[ptr] - 1) % 256
        elif c == '.':
            output.append(chr(tape[ptr]))
        elif c == ',':
            # 忽略输入，使用 0
            tape[ptr] = 0
        elif c == '[':
            if tape[ptr] == 0:
                # 跳过匹配的 ']'
                depth = 1
                while depth > 0:
                    i += 1
                    if i >= n:
                        raise RuntimeError("未匹配的 '['")
                    if code[i] == '[':
                        depth += 1
                    elif code[i] == ']':
                        depth -= 1
        elif c == ']':
            if tape[ptr] != 0:
                # 跳回匹配的 '['
                depth = 1
                while depth > 0:
                    i -= 1
                    if i < 0:
                        raise RuntimeError("未匹配的 ']'")
                    if code[i] == '[':
                        depth -= 1
                    elif code[i] == ']':
                        depth += 1
        # 其他字符（空白等）忽略
        i += 1

    return ''.join(output)


def is_ook(text: str) -> bool:
    """简单检测是否包含 Ook! 关键词"""
    return bool(re.search(r'Ook[.?!]', text))


def main():
    parser = argparse.ArgumentParser(
        description="Ook! / Brainfuck 解释器",
        epilog="从文件或标准输入读取程序，自动检测格式并运行。"
    )
    parser.add_argument(
        "-i", "--input",
        help="输入文件路径（若不指定，则从 stdin 读取）"
    )
    args = parser.parse_args()

    # 读取程序源码
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                source = f.read()
        except FileNotFoundError:
            print(f"错误：文件 '{args.input}' 不存在", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"读取文件出错: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # 从标准输入读取（直到 EOF）
        source = sys.stdin.read()

    if not source.strip():
        print("错误：未输入任何代码", file=sys.stderr)
        sys.exit(1)

    # 自动检测并转换
    try:
        if is_ook(source):
            bf_code = parse_ook(source)
        else:
            # 直接当作 Brainfuck
            # 过滤掉非 BF 指令的字符（仅保留 ><+-.,[]）
            bf_code = ''.join(ch for ch in source if ch in '><+-.,[]')
            if not bf_code:
                raise ValueError("未检测到有效的 Brainfuck 指令")

        # 执行
        output = run_bf(bf_code)
        print(output, end='')  # 输出可能不带换行

    except Exception as e:
        print(f"执行错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
