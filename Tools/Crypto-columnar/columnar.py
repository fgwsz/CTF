#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
项目名称：列置换密码加解密工具 (Columnar Transposition Cipher Tool)
版本：1.1
作者：CTF Learner
描述：
    本工具实现了经典的列置换密码，支持加密、解密以及两种破解方式：
        1) 已知密钥解密：根据给定的数字密钥解密密文。
        2) 暴力枚举破解：在未知密钥的情况下，通过遍历所有可能的密钥长度和排列，
           尝试解密并匹配预设的关键词（如 "flag{"），从而恢复明文。

    加密原理：
        - 将明文按固定宽度（密钥长度）分成若干组，不足时用填充字符补齐。
        - 每组按行写入一个矩阵，根据密钥指定的列顺序逐列读取得到密文。

    解密原理：
        - 将密文按密钥顺序逐列填充回矩阵，再按行读取得到明文（去除填充字符）。

    密钥格式：
        - 密钥是一个包含 1~n 每个数字一次的排列（n 为列数）。
        - 输入格式可以是连续数字字符串（如 "216534"）或空格/逗号分隔的数字（如 "2 1 6 5 3 4"）。

    使用示例：
        # 加密
        python columnar.py encrypt -p "flag{52048c453d794df1}" -k "216534" -f '@'

        # 解密（已知密钥）
        python columnar.py decrypt -c "lf5{ag024c483549d7fd@@1}" -k "216534" -f '@'

        # 暴力破解（自动尝试密钥长度 2~10）
        python columnar.py crack -c "lf5{ag024c483549d7fd@@1}" --keyword "flag{" --max-len 10

    注意事项：
        - 填充字符（-f）必须与加密时使用的相同，否则解密结果可能包含多余字符。
        - 暴力破解时，密钥长度越大排列数激增（n=10时约362万种），建议设置合理的 max-len。
================================================================================
"""

import argparse
import itertools
import sys
import re
from typing import List, Tuple, Optional


class ColumnarCipher:
    """列置换密码加解密器"""

    def __init__(self, key: List[int], filler: str = '@'):
        """
        初始化密码器

        :param key: 密钥排列，例如 [2,1,6,5,3,4]（1索引）
        :param filler: 填充字符，用于补齐分组
        """
        self.key = key
        self.n = len(key)
        self.filler = filler

    def _validate_key(self):
        """检查密钥是否为1~n的排列"""
        if sorted(self.key) != list(range(1, self.n + 1)):
            raise ValueError(f"密钥必须为 1~{self.n} 的排列，当前: {self.key}")

    def _pad_text(self, text: str) -> str:
        """对文本进行填充，使长度为密钥长度的整数倍"""
        remainder = len(text) % self.n
        if remainder != 0:
            pad_len = self.n - remainder
            text += self.filler * pad_len
        return text

    def _unpad_text(self, text: str) -> str:
        """移除末尾的填充字符（仅当填充字符在末尾连续出现时移除）"""
        while text.endswith(self.filler):
            text = text[:-1]
        return text

    def encrypt(self, plaintext: str) -> str:
        """
        加密明文

        算法：
            1. 将明文按列数 n 分组，最后一组不足则填充。
            2. 对每一组，构建 n 列矩阵（按行填充）。
            3. 根据密钥顺序，逐列读取矩阵，拼接为密文。

        :param plaintext: 明文字符串
        :return: 密文字符串
        """
        self._validate_key()
        plaintext = self._pad_text(plaintext)
        groups = [plaintext[i:i + self.n] for i in range(0, len(plaintext), self.n)]
        cipher_parts = []
        for group in groups:
            for col_idx in self.key:
                idx = col_idx - 1
                cipher_parts.append(group[idx])
        return ''.join(cipher_parts)

    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文（已知密钥）

        算法：
            1. 将密文按密钥长度 n 分组。
            2. 对每一组，构建一个 n 列的矩阵（空），根据密钥顺序，将密文各字符按列填充到对应列。
            3. 按行读取矩阵，得到明文字符。
            4. 去除填充字符。

        :param ciphertext: 密文字符串
        :return: 明文字符串
        """
        self._validate_key()
        if len(ciphertext) % self.n != 0:
            raise ValueError(f"密文长度 {len(ciphertext)} 不是密钥长度 {self.n} 的倍数")
        groups = [ciphertext[i:i + self.n] for i in range(0, len(ciphertext), self.n)]
        plain_parts = []
        for group in groups:
            cols = [''] * self.n
            for i, col_idx in enumerate(self.key):
                idx = col_idx - 1
                cols[idx] = group[i]
            plain_parts.append(''.join(cols))
        plaintext = ''.join(plain_parts)
        plaintext = self._unpad_text(plaintext)
        return plaintext

    @staticmethod
    def parse_key(key_str: str) -> List[int]:
        """
        将用户输入的密钥字符串解析为整数列表

        支持格式：
            - "216534"       -> [2,1,6,5,3,4]
            - "2 1 6 5 3 4"  -> [2,1,6,5,3,4]
            - "2,1,6,5,3,4"  -> [2,1,6,5,3,4]

        :param key_str: 密钥字符串
        :return: 整数列表
        """
        key_str = key_str.strip()
        if ',' in key_str:
            parts = key_str.split(',')
        elif ' ' in key_str:
            parts = key_str.split()
        else:
            parts = list(key_str)
        try:
            key = [int(p) for p in parts]
        except ValueError:
            raise ValueError(f"无效的密钥格式: {key_str}，请使用数字排列，如 '216534' 或 '2 1 6 5 3 4'")
        n = len(key)
        if sorted(key) != list(range(1, n+1)):
            raise ValueError(f"密钥必须是1~{n}的排列，当前: {key}")
        return key

    @classmethod
    def brute_force(cls, ciphertext: str, keyword: str = "flag{", max_key_len: int = 10, filler: str = '@') -> List[Tuple[int, List[int], str]]:
        """
        暴力破解列置换密码

        尝试所有可能的密钥长度（从2到max_key_len），对每个长度尝试所有排列，
        解密后检查是否包含keyword（关键字），若包含则记录结果。

        :param ciphertext: 密文字符串
        :param keyword: 用于判别明文的特征字符串（如 "flag{"）
        :param max_key_len: 最大密钥长度（若为None，则尝试2到len(ciphertext)//2）
        :param filler: 填充字符
        :return: 所有成功匹配的结果列表，每个元素为 (密钥长度, 密钥排列, 明文)
        """
        results = []
        if max_key_len is None:
            max_key_len = len(ciphertext) // 2
        if max_key_len > 10:
            print(f"警告: 最大密钥长度 {max_key_len} 过大，排列数可能极其庞大，建议使用较小值。")
        for n in range(2, max_key_len + 1):
            # 如果n较大，排列数可能过多，提示用户
            if n > 8:
                total_perms = 1
                for i in range(2, n+1):
                    total_perms *= i
                print(f"密钥长度 {n}，排列数 {total_perms}，可能需要较长时间...")
            for perm in itertools.permutations(range(1, n+1)):
                key = list(perm)
                try:
                    cipher = cls(key, filler)
                    plain = cipher.decrypt(ciphertext)
                except Exception:
                    continue
                if keyword.lower() in plain.lower():
                    results.append((n, key, plain))
        return results


def main():
    # 创建主解析器，并增加详细的描述
    parser = argparse.ArgumentParser(
        description="列置换密码加解密工具 (Columnar Transposition Cipher Tool)",
        epilog="更多信息请参考项目文档或使用子命令的 -h 查看详细帮助。"
    )
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    # ---------- 加密命令 ----------
    enc_parser = subparsers.add_parser(
        'encrypt',
        help='加密明文',
        description='使用指定的密钥对明文进行列置换加密。'
    )
    enc_parser.add_argument(
        '-p', '--plaintext',
        required=True,
        help='要加密的明文字符串'
    )
    enc_parser.add_argument(
        '-k', '--key',
        required=True,
        help='密钥，例如 "216534" 或 "2 1 6 5 3 4"'
    )
    enc_parser.add_argument(
        '-f', '--filler',
        default='@',
        help='填充字符，用于补齐最后一组，默认为 "@"'
    )

    # ---------- 解密命令（已知密钥） ----------
    dec_parser = subparsers.add_parser(
        'decrypt',
        help='解密（已知密钥）',
        description='使用指定的密钥对密文进行列置换解密。'
    )
    dec_parser.add_argument(
        '-c', '--ciphertext',
        required=True,
        help='要解密的密文字符串'
    )
    dec_parser.add_argument(
        '-k', '--key',
        required=True,
        help='密钥，例如 "216534" 或 "2 1 6 5 3 4"'
    )
    dec_parser.add_argument(
        '-f', '--filler',
        default='@',
        help='填充字符（必须与加密时一致），默认为 "@"'
    )

    # ---------- 暴力破解命令 ----------
    crack_parser = subparsers.add_parser(
        'crack',
        help='暴力破解（未知密钥）',
        description='在未知密钥的情况下，尝试所有可能的密钥长度和排列，\
                    通过匹配关键字来恢复明文。'
    )
    crack_parser.add_argument(
        '-c', '--ciphertext',
        required=True,
        help='要破解的密文字符串'
    )
    crack_parser.add_argument(
        '--keyword',
        default='flag{',
        help='用于匹配明文的关键字（不区分大小写），默认为 "flag{"'
    )
    crack_parser.add_argument(
        '--max-len',
        type=int,
        default=10,
        help='最大密钥长度，默认为10。建议根据密文长度合理设置，防止排列爆炸。'
    )
    crack_parser.add_argument(
        '-f', '--filler',
        default='@',
        help='填充字符（必须与加密时一致），默认为 "@"'
    )

    args = parser.parse_args()

    if args.command == 'encrypt':
        key = ColumnarCipher.parse_key(args.key)
        cipher = ColumnarCipher(key, args.filler)
        plaintext = args.plaintext
        ciphertext = cipher.encrypt(plaintext)
        print(f"加密结果: {ciphertext}")

    elif args.command == 'decrypt':
        key = ColumnarCipher.parse_key(args.key)
        cipher = ColumnarCipher(key, args.filler)
        plaintext = cipher.decrypt(args.ciphertext)
        print(f"解密结果: {plaintext}")

    elif args.command == 'crack':
        results = ColumnarCipher.brute_force(
            args.ciphertext,
            args.keyword,
            args.max_len,
            args.filler
        )
        if not results:
            print("未找到匹配的结果，请尝试增大 max-len 或调整关键字。")
        else:
            print(f"共找到 {len(results)} 个可能的结果：")
            for n, key, plain in results:
                print(f"长度 {n:2d}, 密钥 {''.join(map(str,key))}: {plain}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
