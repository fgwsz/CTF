#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
                    HTML 实体递归解码器 (decode_html_entities.py)
================================================================================

【功能概述】
    将包含 HTML 数字实体（如 &#102;）或命名实体（如 &amp;lt;）的文本，
    递归解码为普通 UTF-8 文本。特别适用于处理多层嵌套实体（例如 &amp;#102;），
    能自动反复解码直到文本不再变化，彻底还原原始内容。

【适用场景】
    - CTF 比赛中遇到被 HTML 实体混淆的 flag。
    - 网页源码中提取被编码的字符串。
    - 处理多层转义的数据（如 &amp;amp;#102; 这种极端情况）。

【输入方式】
    支持两种输入方式：
    1. 从标准输入读取（交互式或管道）：
           python decode_html_entities.py
       然后粘贴内容，按 Ctrl+Z（Windows）或 Ctrl+D（Unix）结束输入。
    2. 从命令行参数指定文本文件路径：
           python decode_html_entities.py encoded.txt

【输出】
    解码后的纯文本内容直接打印到标准输出（终端）。

【使用示例】
    # 示例 1：直接粘贴解码
    $ python decode_html_entities.py
    （粘贴以下内容）
    &amp;#102;&amp;#108;&amp;#97;&amp;#103;&amp;#123;... 
    ^Z   （Windows 下按 Ctrl+Z 回车，Unix 按 Ctrl+D）
    输出：flag{...}

    # 示例 2：从文件解码
    $ echo '&amp;#102;&amp;#108;&amp;#97;&amp;#103;' > encoded.txt
    $ python decode_html_entities.py encoded.txt
    输出：flag

    # 示例 3：管道配合 echo（注意转义）
    $ echo '&amp;#102;' | python decode_html_entities.py
    输出：f

【递归解码原理】
    普通 html.unescape() 只解一层，对于 &amp;#102; 会先变成 &#102; 但不会继续解。
    本脚本循环调用 html.unescape()，每次检查是否变化，最多迭代 10 次，
    保证多层嵌套都能完全展开。

【依赖环境】
    - Python 3.6+ （仅依赖标准库 html 和 sys）
    - 无需安装第三方包，离线可用。

【注意事项】
    - 输入文本中的换行和空格会被保留（但首尾空白会被去除，避免误判空输入）。
    - 如果输入内容特别大（超过几 MB），建议使用文件输入方式，避免终端卡顿。
    - 脚本默认最大迭代 10 次，足够处理绝大多数情况；若遇到超深层嵌套，可修改源码中的 max_iter 参数。

【作者与版本】
    - 创建日期：2026-07-27
    - 版本：1.0
    - 遵循：MIT License（可自由使用、修改、分发）

================================================================================
"""

import sys
import html


def decode_recursive(text, max_iter=10):
    """
    递归解码 HTML 实体，直到文本不再变化。

    Args:
        text (str): 待解码的原始字符串。
        max_iter (int): 最大迭代次数，防止死循环。

    Returns:
        str: 完全解码后的文本。
    """
    for _ in range(max_iter):
        decoded = html.unescape(text)
        if decoded == text:   # 没有变化，说明已完全解码
            break
        text = decoded
    return text


def main():
    # 获取输入内容
    if len(sys.argv) > 1:
        # 从文件读取
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误：文件 '{sys.argv[1]}' 不存在。", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"读取文件失败：{e}", file=sys.stderr)
            sys.exit(1)
    else:
        # 从标准输入读取
        content = sys.stdin.read()

    # 去除首尾空白，但不影响内部换行
    content = content.strip()

    if not content:
        print("警告：输入为空。", file=sys.stderr)
        return

    # 递归解码
    result = decode_recursive(content)
    print(result)


if __name__ == "__main__":
    main()
