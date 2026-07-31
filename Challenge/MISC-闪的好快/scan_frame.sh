#!/bin/bash
shopt -s globstar nullglob dotglob

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
TARGET_DIR="$SCRIPT_DIR/masterGO-fixed-frame"
SCAN_CODE="$SCRIPT_DIR/../../Tools/MISC-scan_code/scan_code.py"
PYTHON="python3"

# 检查目标目录是否存在
if [[ ! -d "$TARGET_DIR" ]]; then
    echo "错误: 目录 '$TARGET_DIR' 不存在" >&2
    exit 1
fi

# 遍历所有`frame`图片
for file in "$TARGET_DIR"/**/*.png; do
    if [[ -f "$file" ]]; then
        echo "文件: $file"
        "$PYTHON" "$SCAN_CODE" -i "$file"
    fi
done
