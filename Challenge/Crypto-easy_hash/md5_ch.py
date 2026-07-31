import hashlib

def compute_md5(char):
    md5_flag = hashlib.md5(char.encode())
    return md5_flag.hexdigest()

if __name__ == '__main__':
    chars="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ{}_"
    for char in chars:
        print(f"char:{char},md5:{compute_md5(char)}");
