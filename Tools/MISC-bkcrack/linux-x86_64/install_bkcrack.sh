#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR"

if [[ ! -d "gitrepo" ]]; then
    mkdir gitrepo
fi

cd gitrepo

if [[ ! -d "bkcrack" ]]; then
    git clone git@github.com:kimci86/bkcrack.git
fi

# 确保 snap 版 cmake 已安装（若已安装则跳过）
if [[ ! -x "/snap/bin/cmake" ]]; then
    sudo snap install cmake --classic
fi

cd bkcrack

# 检查编译产物是否存在（按照你说的路径 install/bkcrack）
if [[ ! -f "install/bkcrack" ]]; then
    /snap/bin/cmake -S . -B build -DCMAKE_INSTALL_PREFIX=install
    /snap/bin/cmake --build build --config Release
    /snap/bin/cmake --build build --config Release --target install
fi

# 把编译好的 bkcrack 复制到脚本所在目录
cp install/bkcrack "$SCRIPT_DIR/"

echo "✅ bkcrack 已就绪，位置：$SCRIPT_DIR/bkcrack"
