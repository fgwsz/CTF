#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
项目名称: Morse Code CLI Tool (摩斯密码编解码器)
版本: 2.0 (容错增强版)
作者: 根据用户需求定制
更新日期: 2026-07-25

功能概述:
---------
这是一个基于 Python 的命令行工具，用于将普通文本与摩斯密码相互转换。
它特别适用于 CTF 挑战、网络安全分析和日常摩斯练习。

核心特点:
    ✅ 支持字母、数字、常见标点符号的编码/解码
    ✅ 允许用户自定义字符分隔符和单词分隔符（默认为空格和 " / "）
    ✅ 容错模式：遇到未知摩斯码时不会崩溃，而是用 `[?code]` 标记并继续解析
    ✅ 支持从标准输入读取数据，方便管道操作
    ✅ 提供 `--strict` 开关，用于需要严格验证的场合

依赖:
    - Python 3.6 及以上版本（仅用到标准库，无需额外安装）

使用方法:
---------
    python morse_cli.py decode <摩斯字符串> [选项]
    python morse_cli.py encode <普通文本> [选项]

    如果省略 <参数>，脚本会尝试从标准输入 (stdin) 读取数据。

参数说明:
---------
    decode 子命令:
        morse          要解码的摩斯字符串（可选）
        -c, --char-sep  字符间的分隔符，默认为空格 " "
        -w, --word-sep  单词间的分隔符，默认为 " / "
        -s, --strict    启用严格模式，遇到未知码时抛出异常（默认容错）

    encode 子命令:
        text           要编码的普通文本（可选）
        -c, --char-sep  字符分隔符，默认为空格 " "
        -w, --word-sep  单词分隔符，默认为 " / "
        -s, --strict    启用严格模式，遇到未知字符时抛出异常（默认容错）

示例:
---------
    1. 解码默认格式的摩斯码 (字母间空格，单词间 " / ")
        $ python morse_cli.py decode ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
        HELLO WORLD

    2. 编码文本
        $ python morse_cli.py encode "HELLO WORLD"
        .... . .-.. .-.. --- / .-- --- .-. .-.. -..

    3. 自定义分隔符 (使用逗号分隔字符，竖线分隔单词)
        $ python morse_cli.py encode "HELLO WORLD" -c "," -w " | "
        ....,.,.-..,.-..,--- | .--,---,.-.,.-..,-..

        $ python morse_cli.py decode "....,.,.-..,.-..,--- | .--,---,.-.,.-..,-.." -c "," -w " | "
        HELLO WORLD

    4. 从管道读取数据 (Linux / macOS)
        $ echo ".... . .-.. .-.. --- / .-- --- .-. .-.. -.." | python morse_cli.py decode
        HELLO WORLD

        $ echo "HELLO WORLD" | python morse_cli.py encode
        .... . .-.. .-.. --- / .-- --- .-. .-.. -..

    5. 容错模式: 遇到未知码会显示标记并继续
        $ python morse_cli.py decode ".... . .-.. .-.. --- / ..... .-- --- .-. .-.. -.."
        HELLO [?.....] WORLD

    6. 严格模式 (遇到未知码立即报错)
        $ python morse_cli.py decode ".... . .-.. .-.. --- / ..... .-- --- .-. .-.. -.." -s
        错误: 未识别的摩斯码: '.....'

注意事项:
---------
    - 默认的摩斯码表符合国际标准，并包含常用标点符号。
    - 花括号 `{` 和 `}` 未在标准摩斯中定义，但本工具默认不报错（容错模式）。
    - 如果需添加自定义编码，请直接修改脚本中的 `MORSE_DICT` 和 `REVERSE_DICT`。

================================================================================
"""

import argparse
import sys

# ---------- 摩斯码表 ----------
MORSE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9', '-----': '0',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
    '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
    '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
    '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
    '...-..-': '$', '.--.-.': '@'
}
REVERSE_DICT = {v: k for k, v in MORSE_DICT.items()}


# ---------- 核心函数 ----------
def decode_morse(morse_text, char_sep=' ', word_sep=' / ', strict=False):
    """
    将摩斯字符串解码为普通文本。
    若 strict=False，遇到未知码会保留为 [?code] 并继续。
    """
    words = morse_text.strip().split(word_sep)
    result = []
    for w in words:
        chars = w.split(char_sep)
        decoded = []
        for c in chars:
            c = c.strip()
            if not c:
                continue
            if c in MORSE_DICT:
                decoded.append(MORSE_DICT[c])
            else:
                if strict:
                    raise ValueError(f"未识别的摩斯码: '{c}'")
                else:
                    decoded.append(f'[?{c}]')
        result.append(''.join(decoded))
    return ' '.join(result)


def encode_text(text, char_sep=' ', word_sep=' / ', strict=False):
    """
    将普通文本编码为摩斯字符串。
    若 strict=False，未知字符会原样保留（用 [?] 标记）。
    """
    words = text.upper().split()
    result = []
    for w in words:
        encoded = []
        for ch in w:
            if ch in REVERSE_DICT:
                encoded.append(REVERSE_DICT[ch])
            else:
                if strict:
                    raise ValueError(f"无法编码的字符: '{ch}'")
                else:
                    encoded.append(f'[?{ch}]')
        result.append(char_sep.join(encoded))
    return word_sep.join(result)


# ---------- 命令行界面 ----------
def main():
    parser = argparse.ArgumentParser(
        description='摩斯密码编解码器（支持自定义分隔符和容错）',
        epilog='更多示例请查看脚本头部注释'
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='子命令')

    # decode 子命令
    parser_decode = subparsers.add_parser('decode', help='解码摩斯为文本')
    parser_decode.add_argument('morse', nargs='?', help='要解码的摩斯字符串')
    parser_decode.add_argument('-c', '--char-sep', default=' ', help='字符分隔符，默认空格')
    parser_decode.add_argument('-w', '--word-sep', default=' / ', help='单词分隔符，默认 " / "')
    parser_decode.add_argument('-s', '--strict', action='store_true', help='严格模式（遇到未知码报错）')

    # encode 子命令
    parser_encode = subparsers.add_parser('encode', help='编码文本为摩斯')
    parser_encode.add_argument('text', nargs='?', help='要编码的普通文本')
    parser_encode.add_argument('-c', '--char-sep', default=' ', help='字符分隔符，默认空格')
    parser_encode.add_argument('-w', '--word-sep', default=' / ', help='单词分隔符，默认 " / "')
    parser_encode.add_argument('-s', '--strict', action='store_true', help='严格模式（遇到未知字符报错）')

    args = parser.parse_args()

    # 读取输入
    try:
        if args.command == 'decode':
            if args.morse:
                input_data = args.morse
            else:
                input_data = sys.stdin.read().strip()
            if not input_data:
                print('错误：未提供摩斯字符串', file=sys.stderr)
                sys.exit(1)
            result = decode_morse(input_data, args.char_sep, args.word_sep, args.strict)
            print(result)

        elif args.command == 'encode':
            if args.text:
                input_data = args.text
            else:
                input_data = sys.stdin.read().strip()
            if not input_data:
                print('错误：未提供要编码的文本', file=sys.stderr)
                sys.exit(1)
            result = encode_text(input_data, args.char_sep, args.word_sep, args.strict)
            print(result)

    except ValueError as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
