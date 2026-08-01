#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
URL 编码/解码命令行工具

功能特性：
----------
- 支持 URL 编码（encode）和解码（decode）两种操作模式
- 可从命令行参数或标准输入（stdin）读取数据，方便在 Shell 管道中使用
- 可选的 --plus 开关：编码时用 '+' 代替空格（兼容 application/x-www-form-urlencoded）
- 可选的 --safe 参数：自定义额外保留的字符（默认保留 -._~）
- 可选的 --encoding 参数：指定字符编码（默认 UTF-8）
- 解码时自动处理非法字节（errors="replace"），不会崩溃

用法：
------
  urlcodec_tool.py encode <字符串> [选项]
  urlcodec_tool.py decode <字符串> [选项]
  cat file.txt | urlcodec_tool.py encode [选项]   # 从 stdin 读取

选项：
------
  --plus          编码时用 '+' 代替空格（仅对 encode 有效）；
                  解码时若指定，则将 '+' 转回空格。
  --safe CHARS    指定额外不编码的字符（例如 --safe="/:."）
  --encoding ENC  指定字符编码（默认 utf-8）

使用示例：
----------
  # 基础编码
  $ ./urlcodec_tool.py encode "Hello World! 你好"
  Hello%20World%21%20%E4%BD%A0%E5%A5%BD

  # 表单风格编码（空格变 '+'）
  $ ./urlcodec_tool.py encode "Hello World" --plus
  Hello+World

  # 保留 URL 结构字符（不编码 '/' 和 ':'）
  $ ./urlcodec_tool.py encode "https://example.com/path" --safe="/:"
  https://example.com/path

  # 解码
  $ ./urlcodec_tool.py decode "Hello%20World%21"
  Hello World!

  # 从管道读取
  $ echo "https://example.com/?q=test" | ./urlcodec_tool.py encode
  https%3A%2F%2Fexample.com%2F%3Fq%3Dtest

  # 批量处理文件
  $ cat urls.txt | ./urlcodec_tool.py encode > encoded_urls.txt

注意事项：
----------
- 该工具基于 Python 标准库 urllib.parse 实现，稳定可靠。
- 若未提供文本且标准输入无数据，程序会报错退出。
- 解码时若指定 --plus，则 '+' 会被还原为空格（适用于表单数据）。
===============================================================================
"""

import sys
import argparse
from typing import Optional
from urllib.parse import quote, unquote, quote_plus, unquote_plus


def encode_text(
    text: str,
    *,
    plus: bool = False,
    safe: str = "",
    encoding: str = "utf-8"
) -> str:
    """
    对文本进行 URL 编码。

    :param text:     待编码的字符串
    :param plus:     若为 True，空格编码为 '+' 而非 '%20'
    :param safe:     额外保留的字符（默认保留 -._~）
    :param encoding: 字符编码（默认 utf-8）
    :return:         编码后的字符串
    """
    if plus:
        return quote_plus(text, safe=safe, encoding=encoding)
    else:
        return quote(text, safe=safe, encoding=encoding)


def decode_text(
    text: str,
    *,
    plus: bool = False,
    encoding: str = "utf-8"
) -> str:
    """
    对 URL 编码的字符串进行解码。

    :param text:     待解码的字符串
    :param plus:     若为 True，将 '+' 转换为空格（表单数据风格）
    :param encoding: 字符编码（默认 utf-8）
    :return:         解码后的字符串
    """
    if plus:
        return unquote_plus(text, encoding=encoding, errors="replace")
    else:
        return unquote(text, encoding=encoding, errors="replace")


def read_input(args_text: Optional[list], stdin_text: Optional[str] = None) -> str:
    """
    从命令行参数或标准输入读取输入文本。

    优先使用命令行参数（args_text 非空），否则尝试从标准输入读取。
    若均无内容，则抛出异常。

    :param args_text:  命令行传入的文本列表（可能为空）
    :param stdin_text: 预先读取的标准输入内容（可选）
    :return:           合并后的输入字符串
    :raises RuntimeError: 当未提供任何输入时抛出
    """
    if args_text:
        # 多个参数用空格连接，保留原始空格（用 join 保留）
        return ' '.join(args_text)
    elif stdin_text is not None and stdin_text.strip():
        return stdin_text
    else:
        # 若未传入 stdin_text，尝试从 sys.stdin 读取
        if not sys.stdin.isatty():
            # 使用 buffer 读取二进制，再按指定编码解码（保留原始字节）
            raw = sys.stdin.buffer.read()
            if raw:
                # 尝试用 UTF-8 解码，遇到错误时替换（但保留原始）
                return raw.decode('utf-8', errors='replace')
        raise RuntimeError("未提供输入文本，且标准输入为空")


def parse_arguments() -> argparse.Namespace:
    """解析并返回命令行参数。"""
    parser = argparse.ArgumentParser(
        description="URL 编码/解码工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="更多信息请查看脚本首部的文档。"
    )
    parser.add_argument(
        "mode",
        choices=["encode", "decode"],
        help="操作模式：encode（编码）或 decode（解码）"
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="要处理的文本（若不提供则从 stdin 读取）"
    )
    parser.add_argument(
        "--plus",
        action="store_true",
        help="编码时用 '+' 代替空格（仅对 encode 有效）；解码时若指定则将 '+' 转回空格"
    )
    parser.add_argument(
        "--safe",
        default="",
        help="编码时额外保留的字符（默认保留 -._~）"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="字符编码（默认 utf-8）"
    )
    return parser.parse_args()


def main() -> None:
    """主函数入口。"""
    args = parse_arguments()

    try:
        input_text = read_input(args.text)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.mode == "encode":
            result = encode_text(
                input_text,
                plus=args.plus,
                safe=args.safe,
                encoding=args.encoding
            )
        else:  # decode
            result = decode_text(
                input_text,
                plus=args.plus,
                encoding=args.encoding
            )
        print(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
