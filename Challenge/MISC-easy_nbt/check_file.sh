#!/bin/bash
script_dir_path=$(dirname "$(readlink -f "$0")")

shopt -s globstar nullglob dotglob

cd "$script_dir_path"

# 遍历 export 下的所有文件(包括隐藏文件)
for file in export/**/*; do
    if [[ -f "$file" ]]; then
        # 检查文件类型
        file "$file"
        # 检查文件的二进制字符串信息是否包含`flag`
        strings "$file" | rg "flag"
    fi
done
