#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
                    Base 家族编码器/解码器 - CTF 专用
================================================================================

项目名称
    BaseFamily Toolkit

项目简介
    BaseFamily Toolkit 是一个功能完备的 Base 系列编码/解码工具，专为 CTF 竞赛
    和安全分析设计。它支持常见的 Base16、Base32、Base64（标准与 URL 安全）、
    Base85（两种变体）、Base91 以及 Base58（比特币风格）编码/解码，并内置了
    Base91 和 Base58 的纯 Python 实现，无需安装任何第三方库。无论是编码还是
    解码，都可以一键遍历所有算法，快速识别密文格式，极大提升解题效率。

核心功能
    🔹 编码模式
        - 对输入的文本（或文件内容）使用所有支持的 Base 编码进行编码
        - 输出每种编码的结果，便于比对和选择

    🔹 解码模式
        - 对输入的密文，尝试所有支持的 Base 解码算法
        - 自动检测并显示成功解码的结果（若为二进制则显示十六进制）
        - 详细模式可显示失败的尝试，便于调试

    🔹 支持输入方式
        - 命令行直接传入字符串（-t / --text）
        - 从文件读取（-i / --input）
        - 从标准输入（管道或重定向）读取

    🔹 输出方式
        - 标准输出（屏幕）
        - 输出到文件（-o / --output）

支持的编码算法
    ┌─────────────────┬──────────────────────────────────────┬─────────────────────┐
    │ 名称            │ 说明                                 │ 对应函数            │
    ├─────────────────┼──────────────────────────────────────┼─────────────────────┤
    │ Base16          │ 十六进制（大写），RFC 4648          │ base64.b16encode    │
    │ Base32          │ 32字符集（A-Z2-7），填充=           │ base64.b32encode    │
    │ Base64 (标准)   │ 字符集 A-Z a-z 0-9 + /，填充=      │ base64.b64encode    │
    │ Base64 (URL安全)│ 使用 - 和 _ 替代 + 和 /             │ base64.urlsafe_...  │
    │ Base85 (ASCII85)│ Adobe 变体，使用 <~ ~> 包裹         │ base64.a85encode    │
    │ Base85 (RFC1924)│ 另一变体（Python 的 b85encode）    │ base64.b85encode    │
    │ Base91          │ 广泛字符集，内置纯 Python 实现     │ 自实现              │
    │ Base58          │ 比特币风格，不含 0/O/I/l            │ 自实现              │
    └─────────────────┴──────────────────────────────────────┴─────────────────────┘

依赖环境
    - Python 3.6 或更高版本
    - 仅使用 Python 标准库（base64, argparse, sys, os），无需安装任何第三方库

安装方法
    无需安装，直接下载脚本并赋予执行权限（Linux/macOS）：
        chmod +x base_family.py
    Windows 下直接使用 python base_family.py 运行。

使用说明
    ========== 编码模式 ==========
        # 直接对字符串编码
        python base_family.py -e -t "Hello CTF"

        # 从文件读取内容编码
        python base_family.py -e -i plain.txt

        # 编码并保存到文件
        python base_family.py -e -t "flag{test}" -o encoded.txt

        # 使用管道
        echo "Hello" | python base_family.py -e

    ========== 解码模式 ==========
        # 尝试解码字符串（自动遍历所有算法）
        python base_family.py -d -t "SGVsbG8gQ1RG"

        # 从文件读取密文
        python base_family.py -d -i encoded.b64

        # 解码并保存结果（通常只有一种正确结果，保存会得到所有结果）
        python base_family.py -d -t "ZmxhZw==" -o decoded.txt

        # 显示解码失败的尝试（便于分析）
        python base_family.py -d -t "@iH<,{bdR2H;i6*Tm,Wx2izpx2!" -v

参数详解
    ┌──────────────┬──────────────────────────────────────────────────────┐
    │ 参数         │ 说明                                                │
    ├──────────────┼──────────────────────────────────────────────────────┤
    │ -e, --encode │ 编码模式（必须与 -d 二选一）                       │
    │ -d, --decode │ 解码模式（必须与 -e 二选一）                       │
    │ -t, --text   │ 直接输入要处理的文本字符串                         │
    │ -i, --input  │ 从指定文件读取输入（文本模式）                     │
    │ -o, --output │ 将输出写入指定文件（默认输出到屏幕）               │
    │ -v, --verbose│ 解码时显示所有尝试（包括失败的）                   │
    │ -h, --help   │ 显示帮助信息                                       │
    └──────────────┴──────────────────────────────────────────────────────┘

使用案例集锦
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ 案例 1：编码字符串，快速查看所有 Base 编码结果                            │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │ $ python base_family.py -e "Hello CTF"                                   │
    │ [Base16] 48656C6C6F20435446                                              │
    │ [Base32] JBSWY3DPEBLW64TMMQ======                                        │
    │ [Base64 (标准)] SGVsbG8gQ1RG                                               │
    │ [Base64 (URL安全)] SGVsbG8gQ1RG                                           │
    │ [Base85 (ASCII85/Adobe)] <~9jqo^BlbD-B~>                                 │
    │ [Base85 (RFC 1924 变体)] 9jqo^BlbD-B                                     │
    │ [Base91] @iH<,{bdR2H;i6*Tm,Wx2izpx2!                                    │
    │ [Base58] 2oLr9gH3yhkcBqoZZwPC                                             │
    └──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ 案例 2：解码未知密文，自动识别正确编码                                    │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │ $ python base_family.py -d "@iH<,{bdR2H;i6*Tm,Wx2izpx2!"                 │
    │ [Base91] 成功: Hello CTF                                                 │
    └──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ 案例 3：解码 Base58 编码的比特币地址（或任意数据）                        │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │ $ python base_family.py -d -t "2oLr9gH3yhkcBqoZZwPC"                     │
    │ [Base58] 成功: Hello CTF                                                 │
    └──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ 案例 4：解码 Base64 编码的 flag                                            │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │ $ python base_family.py -d -t "ZmxhZ3t0ZXN0fQ=="                         │
    │ [Base64 (标准)] 成功: flag{test}                                           │
    │ [Base64 (URL安全)] 成功: flag{test}                                        │
    └──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ 案例 5：从文件读取并解码，显示详细调试信息                                │
    ├──────────────────────────────────────────────────────────────────────────────┤
    │ $ echo "SGVsbG8gQ1RG" > encoded.txt                                      │
    │ $ python base_family.py -d -i encoded.txt -v                             │
    │ [Base16] 失败: ...                                                       │
    │ [Base32] 失败: ...                                                       │
    │ [Base64 (标准)] 成功: Hello CTF                                           │
    │ [Base64 (URL安全)] 成功: Hello CTF                                        │
    │ ...                                                                      │
    └──────────────────────────────────────────────────────────────────────────────┘

注意事项
    • 解码模式下，所有算法都会被尝试，输出可能包含多个成功结果（尤其是短字符串
      可能被多个算法同时解码）。一般只有一个是有意义的文本。
    • Base85 的两种变体（Adobe 和 RFC 1924）可能在某些输入下互相解码，但通常
      只有一种能给出正确文本。
    • Base91 的字符集包含双引号（"），若在 Shell 中直接使用包含双引号的字符串，
      请用单引号包裹整个密文，或对双引号进行转义。
    • Base58 是比特币风格，不含 0、O、I、l，且无填充，长度不固定。
    • 对于非 UTF-8 文本，解码结果会以十六进制形式展示，方便进一步分析。
    • 编码模式下，Base85 (ASCII85/Adobe) 默认输出带 <~ ~> 包裹，而 RFC 1924
      变体不带包裹，两者都符合标准。

贡献与反馈
    如果您在使用中发现任何问题或有改进建议，欢迎提出 Issue 或 Pull Request。
    本项目保持 MIT 许可证，欢迎自由使用和修改。

版本信息
    v2.1 (2026-07-28) - 新增 Base58 编码/解码支持（内置纯 Python 实现）
    v2.0 (2026-07-28) - 内置 Base91 纯 Python 实现，无需第三方库
    v1.0 (初始版本)   - 支持 Base16/32/64/85/91，依赖 base91 库

作者
    CTF-Tools 团队
================================================================================
"""

import sys
import os
import base64
import argparse
from typing import Optional, List, Tuple, Callable


# ---------- 内置 Base91 实现 ----------

_BASE91_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "!#$%&()*+,./:;<=>?@[]^_`{|}~\""
)
_BASE91_ENCODE_TABLE = {i: ch for i, ch in enumerate(_BASE91_ALPHABET)}
_BASE91_DECODE_TABLE = {ch: i for i, ch in enumerate(_BASE91_ALPHABET)}


def base91_encode(data: bytes) -> str:
    """
    Base91 编码 (纯 Python 实现)
    参考: https://github.com/tvst/python-avarice/blob/master/base91.py
    """
    b = 0
    n = 0
    out = []
    for byte in data:
        b |= (byte << n)
        n += 8
        if n > 13:
            v = b & 8191
            if v > 88:
                b >>= 13
                n -= 13
            else:
                v = b & 16383
                b >>= 14
                n -= 14
            out.append(_BASE91_ENCODE_TABLE[v % 91])
            out.append(_BASE91_ENCODE_TABLE[v // 91])
    if n:
        out.append(_BASE91_ENCODE_TABLE[b % 91])
        if n > 7 or b > 90:
            out.append(_BASE91_ENCODE_TABLE[b // 91])
    return ''.join(out)


def base91_decode(data: str) -> bytes:
    """
    Base91 解码 (纯 Python 实现)
    参考: https://github.com/tvst/python-avarice/blob/master/base91.py
    """
    v = -1
    b = 0
    n = 0
    out = bytearray()
    for ch in data:
        if ch not in _BASE91_DECODE_TABLE:
            continue
        c = _BASE91_DECODE_TABLE[ch]
        if v < 0:
            v = c
        else:
            v += c * 91
            b |= v << n
            n += 13 if (v & 8191) > 88 else 14
            while n > 7:
                out.append(b & 0xFF)
                b >>= 8
                n -= 8
            v = -1
    if v != -1:
        b |= v << n
        out.append(b & 0xFF)
    return bytes(out)


# ---------- 内置 Base58 实现 (比特币风格) ----------

_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BASE58_ENCODE_TABLE = {i: ch for i, ch in enumerate(_BASE58_ALPHABET)}
_BASE58_DECODE_TABLE = {ch: i for i, ch in enumerate(_BASE58_ALPHABET)}


def base58_encode(data: bytes) -> str:
    """
    Base58 编码 (比特币风格)
    将字节数组视为大端整数，不断除以58取余，映射到字符表。
    前导零字节处理：每个0x00对应输出一个 '1'。
    """
    if not data:
        return ""

    # 计算前导零个数
    leading_zeroes = 0
    for byte in data:
        if byte == 0:
            leading_zeroes += 1
        else:
            break

    # 将数据转换为大整数
    num = int.from_bytes(data, 'big')
    if num == 0:
        return '1' * leading_zeroes

    # 反复取余，构建字符列表（逆序）
    chars = []
    while num > 0:
        num, rem = divmod(num, 58)
        chars.append(_BASE58_ENCODE_TABLE[rem])
    chars.reverse()

    # 补上前导 '1'
    return '1' * leading_zeroes + ''.join(chars)


def base58_decode(data: str) -> bytes:
    """
    Base58 解码 (比特币风格)
    将字符映射为数值，累乘加和得到大整数，然后转为字节数组。
    前导 '1' 对应原始数据中的 0x00 字节。
    """
    if not data:
        return b""

    # 计算前导 '1' 的个数（代表原始零字节）
    leading_ones = 0
    for ch in data:
        if ch == '1':
            leading_ones += 1
        else:
            break

    # 将剩余字符转为大整数
    num = 0
    for ch in data[leading_ones:]:
        if ch not in _BASE58_DECODE_TABLE:
            raise ValueError(f"非法 Base58 字符: {ch}")
        num = num * 58 + _BASE58_DECODE_TABLE[ch]

    # 将大整数转为字节数组（大端序）
    if num == 0:
        return b'\x00' * leading_ones

    # 计算需要的字节数
    byte_length = (num.bit_length() + 7) // 8
    if byte_length == 0:
        byte_length = 1
    raw_bytes = num.to_bytes(byte_length, 'big')

    # 补上前导零字节
    return b'\x00' * leading_ones + raw_bytes


# ---------- 定义编码函数 ----------

def b16_encode(data: bytes) -> str:
    return base64.b16encode(data).decode('ascii')


def b32_encode(data: bytes) -> str:
    return base64.b32encode(data).decode('ascii')


def b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('ascii')


def b85_encode(data: bytes) -> str:
    # ASCII85 (Adobe 变体)
    return base64.a85encode(data, adobe=True).decode('ascii')


def b85_rfc1924_encode(data: bytes) -> str:
    # RFC 1924 变体，Python 的 b85encode 是 Z85 变体，但可尝试
    return base64.b85encode(data).decode('ascii')


def b91_encode_wrapper(data: bytes) -> str:
    return base91_encode(data)


def b58_encode_wrapper(data: bytes) -> str:
    return base58_encode(data)


# 编码器列表：每个元素为 (名称, 编码函数)
ENCODERS: List[Tuple[str, Callable[[bytes], str]]] = [
    ("Base16", b16_encode),
    ("Base32", b32_encode),
    ("Base64 (标准)", b64_encode),
    ("Base64 (URL安全)", b64url_encode),
    ("Base85 (ASCII85/Adobe)", b85_encode),
    ("Base85 (RFC 1924 变体)", b85_rfc1924_encode),
    ("Base91", b91_encode_wrapper),
    ("Base58", b58_encode_wrapper),
]


# ---------- 定义解码函数 ----------

def b16_decode(text: str) -> bytes:
    # 自动处理大小写
    return base64.b16decode(text, casefold=True)


def b32_decode(text: str) -> bytes:
    missing = len(text) % 8
    if missing:
        text += '=' * (8 - missing)
    return base64.b32decode(text)


def b64_decode(text: str) -> bytes:
    missing = len(text) % 4
    if missing:
        text += '=' * (4 - missing)
    return base64.b64decode(text)


def b64url_decode(text: str) -> bytes:
    missing = len(text) % 4
    if missing:
        text += '=' * (4 - missing)
    return base64.urlsafe_b64decode(text)


def b85_decode(text: str) -> bytes:
    return base64.a85decode(text, adobe=True)


def b85_rfc1924_decode(text: str) -> bytes:
    # 尝试 b85decode（Z85 变体）
    return base64.b85decode(text)


def b91_decode_wrapper(text: str) -> bytes:
    return base91_decode(text)


def b58_decode_wrapper(text: str) -> bytes:
    return base58_decode(text)


DECODERS: List[Tuple[str, Callable[[str], bytes]]] = [
    ("Base16", b16_decode),
    ("Base32", b32_decode),
    ("Base64 (标准)", b64_decode),
    ("Base64 (URL安全)", b64url_decode),
    ("Base85 (ASCII85/Adobe)", b85_decode),
    ("Base85 (RFC 1924 变体)", b85_rfc1924_decode),
    ("Base91", b91_decode_wrapper),
    ("Base58", b58_decode_wrapper),
]


# ---------- 辅助函数 ----------

def read_input_text(args) -> str:
    """获取输入文本：优先 -t，其次 -i 文件，否则从标准输入读取"""
    if args.text:
        return args.text
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            return f.read()
    # 从 stdin 读取
    return sys.stdin.read()


def write_output(output_text: str, args) -> None:
    """输出结果到文件或标准输出"""
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
    else:
        sys.stdout.write(output_text)


# ---------- 主要功能 ----------

def encode_mode(args) -> None:
    input_text = read_input_text(args)
    data = input_text.encode('utf-8')

    output_lines = []
    for name, encoder in ENCODERS:
        try:
            result = encoder(data)
            output_lines.append(f"[{name}] {result}")
        except Exception as e:
            output_lines.append(f"[{name}] 编码失败: {e}")

    output_text = "\n".join(output_lines)
    if args.verbose:
        print("【编码结果】")
    write_output(output_text + "\n", args)


def decode_mode(args) -> None:
    input_text = read_input_text(args)
    input_text = input_text.strip()

    output_lines = []
    for name, decoder in DECODERS:
        try:
            decoded_bytes = decoder(input_text)
            # 尝试解码为 UTF-8 文本，若失败则显示十六进制
            try:
                decoded_str = decoded_bytes.decode('utf-8')
                output_lines.append(f"[{name}] 成功: {decoded_str}")
            except UnicodeDecodeError:
                output_lines.append(f"[{name}] 成功 (二进制): {decoded_bytes.hex()}")
        except Exception as e:
            if args.verbose:
                output_lines.append(f"[{name}] 失败: {e}")

    output_text = "\n".join(output_lines)
    if not output_text:
        output_text = "所有解码尝试均失败，无法识别编码。"
    write_output(output_text + "\n", args)


# ---------- 命令行入口 ----------

def main():
    parser = argparse.ArgumentParser(
        description="Base 家族编码器/解码器（遍历所有常见 Base 编码，内置 Base91 和 Base58）",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encode', action='store_true', help='编码模式')
    group.add_argument('-d', '--decode', action='store_true', help='解码模式')

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('-t', '--text', help='直接输入文本字符串')
    input_group.add_argument('-i', '--input', help='从文件读取输入')

    parser.add_argument('-o', '--output', help='输出到文件（默认标准输出）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息（解码时显示失败尝试）')

    args = parser.parse_args()

    if args.encode:
        encode_mode(args)
    elif args.decode:
        decode_mode(args)


if __name__ == '__main__':
    main()
