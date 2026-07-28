#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
                        Base64 编码/解码工具 - CTF 专用版
================================================================================

项目名称
    Base64 Toolkit

项目简介
    一个功能全面、开箱即用的 Base64 编解码工具，专为 CTF 竞赛和日常安全分析设计。
    支持标准 Base64 (RFC 4648) 和 URL 安全 Base64 编码/解码，并提供多种实用选项，
    灵活应对各种题目场景。

核心功能
    🔹 标准 Base64 编码/解码 (字符集: A-Z a-z 0-9 + /)
    🔹 URL 安全 Base64 编码/解码 (字符集: A-Z a-z 0-9 - _)
    🔹 支持三种输入方式（命令行字符串 / 文件 / 标准输入）
    🔹 支持输出到文件或终端
    🔹 编码时可选择移除填充符 '=' (CTF 常见需求)
    🔹 解码时可自动忽略无效字符（如空格、换行、制表符）
    🔹 自动处理缺失的填充符（解码时补齐）
    🔹 当解码结果为二进制数据时，自动转换为十六进制显示
    🔹 完全基于 Python 标准库，无需安装额外依赖

适用场景
    • CTF 中常见的 Base64 编码/解码类题目
    • 处理 Web 参数、Cookie、JWT 中的 Base64 片段
    • 逆向工程中分析加密数据
    • 批量处理文件中的 Base64 内容
    • 快速验证和调试编码数据

依赖环境
    - Python 3.6 或更高版本（仅需标准库）

安装方法
    无需安装，下载脚本后直接在终端运行：
        chmod +x base64_tool.py   (Linux/macOS)
        python base64_tool.py     (Windows)

快速开始
    # 编码字符串
    python base64_tool.py -e "Hello CTF"

    # 解码字符串
    python base64_tool.py -d "SGVsbG8gQ1RG"

    # URL 安全编码
    python base64_tool.py -e "https://example.com" --url-safe

    # 无填充编码（常用于 JWT）
    python base64_tool.py -e "admin" --no-padding

    # 解码时忽略空格和换行
    python base64_tool.py -d "SGVs bG8gV29ybGQ=" --ignore-invalid

    # 从文件读取并编码
    python base64_tool.py -e -i plain.txt -o encoded.b64

    # 从管道读取（Linux）
    echo "flag{test}" | python base64_tool.py -e

    # 解码并自动处理二进制结果（转为 hex）
    python base64_tool.py -d "iVBORw0KGgo..."   # 输出 hex 格式

参数说明
    ┌─────────────────┬──────────────────────────────────────────────────────┐
    │ 参数             │ 说明                                                 │
    ├─────────────────┼──────────────────────────────────────────────────────┤
    │ -e, --encode    │ 编码模式（二选一，必需）                           │
    │ -d, --decode    │ 解码模式（二选一，必需）                           │
    │ data            │ 位置参数，要处理的字符串（优先级最高）             │
    │ -i, --input     │ 输入文件路径（当未提供 data 时生效）              │
    │ -o, --output    │ 输出文件路径（默认输出到屏幕）                    │
    │ --url-safe      │ 使用 URL 安全字符集 (-_ 替代 +/)                  │
    │ --no-padding    │ 编码时移除末尾的 '=' 填充符                       │
    │ --ignore-invalid│ 解码时自动过滤非 Base64 字符（如空格、换行）      │
    │ -h, --help      │ 显示帮助信息                                       │
    └─────────────────┴──────────────────────────────────────────────────────┘

输入优先级
    1. 命令行位置参数 data（如 python tool.py -e "abc"）
    2. 输入文件（-i file.txt）
    3. 标准输入（管道或键盘输入）

使用案例集锦
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 1：标准编码/解码                                                       │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ python base64_tool.py -e "CTF{flag}"                                    │
    │ Q1RGe2ZsYWd9                                                              │
    │ $ python base64_tool.py -d "Q1RGe2ZsYWd9"                                │
    │ CTF{flag}                                                                 │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 2：URL 安全编码（替换 +/ 为 -_）                                    │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ python base64_tool.py -e "https://example.com?q=hello world" --url-safe │
    │ aHR0cHM6Ly9leGFtcGxlLmNvbT9xPWhlbGxvIHdvcmxk                              │
    │ # 注意：URL 安全编码结果不含 / 和 +，可直接用于 URL 参数                │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 3：无填充编码（常见于 JWT 和某些 CTF 题）                           │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ python base64_tool.py -e "admin" --no-padding                           │
    │ YWRtaW4   # 正常应为 YWRtaW4=，这里去掉了 =                              │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 4：解码时处理包含空格的 Base64 字符串（如从网页复制）              │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ python base64_tool.py -d "SGVs bG8g V29y bGQ=" --ignore-invalid        │
    │ Hello World                                                               │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 5：从文件读取并编码，保存到文件                                     │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ echo "Secret data" > input.txt                                         │
    │ $ python base64_tool.py -e -i input.txt -o output.b64                    │
    │ $ cat output.b64                                                          │
    │ U2VjcmV0IGRhdGE=                                                          │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 6：解码二进制数据（如图片）并显示十六进制                           │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ python base64_tool.py -d "iVBORw0KGgoAAAANSUhEUgAAAAUA..."             │
    │ [提示] 解码结果不是有效 UTF-8 文本，已转十六进制显示                     │
    │ 89504e470d0a1a0a0000000d49484452...                                      │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 7：管道组合使用（配合 grep、curl 等）                               │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ curl -s http://example.com/api | python base64_tool.py -d              │
    │ # 将 API 返回的 Base64 内容直接解码                                      │
    └─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ 案例 8：批量处理多个 Base64 字符串（借助 xargs）                         │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ $ echo "Q1RG" "SGVsbG8=" | xargs -n1 python base64_tool.py -d            │
    │ CTF                                                                       │
    │ Hello                                                                     │
    └─────────────────────────────────────────────────────────────────────────────┘

注意事项
    • 解码时如果结果不是合法的 UTF-8 文本，将自动转换为十六进制字符串输出，
      以免终端乱码。
    • 使用 -o 输出到文件时，若解码结果为二进制数据，文件将包含原始字节，
      但本工具以文本模式输出，如需严格二进制请自行扩展。
    • URL 安全模式编码的结果仍包含填充 '='（除非使用 --no-padding），
      部分场景（如 JWT）需要移除填充，请使用 --no-padding 组合。
    • 如果输入数据很大，建议使用文件输入而非命令行参数，以避免 shell 长度限制。

作者信息
    CTF-Tools 团队
    版本：v2.0
    最后更新：2025-07-28

许可证
    本项目采用 MIT 许可证，可自由使用和修改。
================================================================================
"""

import sys
import base64
import argparse


def get_input_data(args) -> str:
    """
    获取输入数据，优先级：
    1. 命令行位置参数 (args.data)
    2. 输入文件 (args.input)
    3. 标准输入 (stdin)
    """
    if args.data:
        return args.data
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            return f.read()
    # 从标准输入读取（支持管道）
    return sys.stdin.read()


def safe_b64encode(data: bytes, url_safe: bool, no_padding: bool) -> str:
    """Base64 编码，支持 URL 安全和无填充"""
    if url_safe:
        encoded = base64.urlsafe_b64encode(data).decode('ascii')
    else:
        encoded = base64.b64encode(data).decode('ascii')
    if no_padding:
        encoded = encoded.rstrip('=')
    return encoded


def safe_b64decode(data: str, url_safe: bool, ignore_invalid: bool) -> bytes:
    """Base64 解码，支持 URL 安全，忽略无效字符，自动补齐填充"""
    if ignore_invalid:
        if url_safe:
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=')
        else:
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        data = ''.join(ch for ch in data if ch in valid_chars)

    # 自动补齐填充 '=' 到 4 的倍数
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)

    try:
        if url_safe:
            return base64.urlsafe_b64decode(data)
        else:
            return base64.b64decode(data, validate=True)
    except Exception as e:
        raise ValueError(f"解码失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Base64 编解码工具 - 支持标准/URL安全，命令行/文件/管道输入",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 互斥操作：编码或解码（必需）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encode', action='store_true', help='编码模式')
    group.add_argument('-d', '--decode', action='store_true', help='解码模式')

    # 位置参数：要处理的字符串（可选，优先级最高）
    parser.add_argument('data', nargs='?', help='要处理的字符串（若提供则优先使用）')

    # 其他选项
    parser.add_argument('-i', '--input', help='输入文件路径（当未提供 data 时使用）')
    parser.add_argument('-o', '--output', help='输出文件路径（默认输出到标准输出）')
    parser.add_argument('--url-safe', action='store_true', help='使用 URL 安全字符集 (-_ 替代 +/)')
    parser.add_argument('--no-padding', action='store_true', help='编码时不添加填充 "="')
    parser.add_argument('--ignore-invalid', action='store_true', help='解码时忽略非 Base64 字符')

    args = parser.parse_args()

    try:
        # 获取输入数据
        raw_input = get_input_data(args)

        if args.encode:
            input_bytes = raw_input.encode('utf-8')
            result = safe_b64encode(input_bytes, args.url_safe, args.no_padding)
        else:  # decode
            decoded_bytes = safe_b64decode(raw_input, args.url_safe, args.ignore_invalid)
            try:
                result = decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # 如果不是合法 UTF-8，转为十六进制字符串
                result = decoded_bytes.hex()
                print("[提示] 解码结果不是有效 UTF-8 文本，已转十六进制显示", file=sys.stderr)

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            sys.stdout.write(result)
            # 如果输出到终端，且末尾没有换行，补一个换行符
            if sys.stdout.isatty() and not result.endswith('\n'):
                sys.stdout.write('\n')

    except FileNotFoundError as e:
        print(f"[错误] 文件不存在: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
