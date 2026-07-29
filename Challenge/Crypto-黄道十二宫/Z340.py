#!/usr/bin/env python3
# -*-coding:utf8-*-

# Z340 黄道十二宫重排脚本 - 从 input.txt 加载原始矩阵
def reorder_zodiac(origin_lines, rows=9, cols=15):
    # 构建原始二维矩阵，清除每行空格
    grid = []
    for line in origin_lines:
        line = line.strip()
        s = line.replace(" ", "")
        grid.append(list(s))
    
    mid_matrix = []  # 15行9列 中间矩阵
    # 遍历每一个起点列 n (0~14)，对应中间矩阵第n行
    for start_c in range(cols):
        cur_r = 0
        cur_c = start_c
        line_buf = []
        # 每条对角线取9个字符
        for _ in range(rows):
            line_buf.append(grid[cur_r][cur_c])
            # 步进：下1行，右2列，模循环
            cur_r = (cur_r + 1) % rows
            cur_c = (cur_c + 2) % cols
        mid_matrix.append(line_buf)
    
    # 中间矩阵按行从小到大拼接成单行密文
    final = ""
    for line in mid_matrix:
        final += "".join(line)
    return final

if __name__ == "__main__":
    # 从 input.txt 读取原始矩阵
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            raw_data = f.readlines()
    except FileNotFoundError:
        print("错误：未找到 input.txt 文件，请将原始矩阵放入同目录 input.txt！")
        exit(1)

    cipher = reorder_zodiac(raw_data, rows=9, cols=15)
    print("=== 最终重排密文 ===")
    print(cipher)

    # 输出到 cipher.txt 供 AZdecrypt 使用
    with open("cipher.txt", "w", encoding="utf-8") as f:
        f.write(cipher)
    print("\n已将重排结果保存至 cipher.txt")
