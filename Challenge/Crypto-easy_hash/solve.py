# -*- coding:utf-8 -*-
import hashlib

def compute_md5(char):
    md5_flag = hashlib.md5(char.encode())
    return md5_flag.hexdigest()

if __name__ == '__main__':
    # 构建匹配字典
    match_map={}
    chars="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ{}_"
    for char in chars:
        match_map[compute_md5(char)]=str(char)

    # 自动匹配export/output所有行md5哈希对应的单字符
    with open("export/output","r") as output:
        lines=output.read().splitlines() #按行分隔为字符串列表,去除尾部换行回车
        for line in lines:
            if line in match_map:
                print(match_map[line],end='')#字符间不换行
            else:
                print("\nmd5 key不存在,需要补全chars")

    # 换行
    print()
