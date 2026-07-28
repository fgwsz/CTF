#!/bin/bash
set -euo pipefail

# 脚本所在目录
script_dir=$(dirname "$(readlink -f "$0")")
cd "$script_dir"

# 解压输出根目录
output_root="export/extracted"
mkdir -p "$output_root"

# 遍历 export 下所有普通文件（包括隐藏文件）
find export -type f -print0 | while IFS= read -r -d '' file; do
    # 用 file 命令检测 MIME 类型，识别 gzip
    if file -b --mime-type "$file" | grep -q '^application/gzip$'; then
        echo "正在解压: $file"

        # 构造输出路径：保留相对目录结构，添加 .extracted 后缀以防重名
        relative_path="${file#export/}"          # 去掉 export/ 前缀
        target="$output_root/$relative_path.extracted"
        target_dir="$(dirname "$target")"
        mkdir -p "$target_dir"

        # 解压到目标文件（-c 输出到 stdout，重定向）
        if gunzip -c "$file" > "$target" 2>/dev/null; then
            echo "  解压成功 -> $target"
        else
            echo "  解压失败: $file" >&2
        fi
    fi
done

echo "全部处理完毕，解压文件位于: $output_root"
