#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
import base64

# Base64 标准字符集（用于合法性检查）
B64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def is_readable(data: bytes) -> bool:
    """检查解码结果是否全部为可打印 ASCII（或包含常见 flag 格式）"""
    # 先检查是否包含 flag
    if b"flag{" in data.lower() or b"ctf{" in data.lower():
        return True
    # 否则检查是否全部可打印（含空格）
    return all(32 <= b <= 126 for b in data)

def solve():
    # 给定的大写串
    upper = "QWIHBLGZZXJSXZNVBZW"

    # 每个大写字符可能的原始字符（数字或大小写字母，所有均属于 Base64 字符集）
    mapping = {
        'Q': ['4', '9', 'Q', 'q'],
        'W': ['W', 'w'],
        'I': ['1', 'I', 'i'],          # 大写 I 不常见但可作为候选
        'H': ['H', 'h'],
        'B': ['8', 'B', 'b'],
        'L': ['1', 'L', 'l'],               # L/l 都可能是 1
        'G': ['6', '9', 'G', 'g'],
        'Z': ['2', 'Z', 'z'],
        'X': ['X', 'x'],
        'J': ['J', 'j'],
        'S': ['5', 'S', 's'],
        'N': ['N', 'n'],
        'V': ['V', 'v'],
    }

    # 构建每个位置的候选列表
    options = []
    for ch in upper:
        if ch in mapping:
            opts = mapping[ch]
            # 过滤出属于 Base64 字符集的（其实都是）
            opts = [c for c in opts if c in B64_CHARS]
            if not opts:
                opts = [ch]   # 保底
            options.append(opts)
        else:
            options.append([ch])

    total = 1
    for opts in options:
        total *= len(opts)
    print(f"[*] 待枚举候选组合数: {total:,}")

    found = []
    count = 0

    for combo in itertools.product(*options):
        count += 1
        if count % 200000 == 0:
            print(f"[*] 已尝试 {count:,} 个组合...")

        cand = "".join(combo)

        # Base64 解码需要长度是 4 的倍数，尝试补 0~3 个 '=' 
        for pad in range(4):
            test_str = cand + "=" * pad
            try:
                raw = base64.b64decode(test_str, validate=True)
            except Exception:
                continue

            if is_readable(raw):
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = str(raw)
                found.append((test_str, text))
                # 如果包含 flag 则优先输出并结束
                if "flag{" in text.lower() or "ctf{" in text.lower():
                    print(f"[+] 找到 flag: {test_str} -> {text}")
                    return

    if not found:
        print("[*] 未找到可读结果，请尝试调整候选映射或编码方式。")
    else:
        print(f"\n[*] 共找到 {len(found)} 个可读结果（含 flag 或可打印 ASCII）：")
        for s, text in found:
            print(f"    {s} -> {text}")

if __name__ == "__main__":
    solve()
