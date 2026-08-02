import re

with open('morse-1-decode.txt', 'r') as f:
    text = f.read()

# 提取所有有效的解码字符（忽略 [?.--.-] 和空格）
chars = re.findall(r'[0-9A-FU]', text)   # 只取数字、A-F、U
s = ''.join(chars)

# 按 "U" 分割，每个 U 后跟四个十六进制字符
codes = []
i = 0
while i < len(s):
    if s[i] == 'U':
        if i+4 < len(s):
            code = s[i+1:i+5]
            # 确保都是十六进制字符
            if all(c in '0123456789ABCDEF' for c in code):
                codes.append(code)
                i += 5
            else:
                i += 1
        else:
            break
    else:
        i += 1

# 解码为 Unicode 字符串
result = ''.join(chr(int(code, 16)) for code in codes)
print(result)
