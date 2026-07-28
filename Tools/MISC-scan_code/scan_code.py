#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
========================================================================
跨平台二维码/条形码扫描器 (CTF专用) - 完整版 v3.1
========================================================================

功能：
    - 支持多种图片格式
    - 使用 pyrxing（推荐）解码 QR Code, Data Matrix, Aztec, UPC, EAN, Code 128, Code 39 等
    - 自动回退到 OpenCV QR 解码器（仅 QR）
    - 可选预处理（去噪、二值化、形态学）
    - 自适应属性访问，兼容 pyrxing 不同版本

依赖安装：
    pip install pyrxing opencv-python numpy Pillow

用法：
    python scan_code.py -i image.jpg [-p] [-o debug.png] [-v]

作者: CTF-Scanner
版本: 3.1
========================================================================
"""

import argparse
import sys
import cv2
import numpy as np
from PIL import Image

# 尝试导入 pyrxing
try:
    import pyrxing
    PYRXING_AVAILABLE = True
except ImportError:
    PYRXING_AVAILABLE = False
    print("[警告] pyrxing 未安装，将使用 OpenCV 备选（仅 QR 码）", file=sys.stderr)
    print("[提示] 推荐安装: pip install pyrxing", file=sys.stderr)


def preprocess_image(img, verbose=False):
    """图像预处理：灰度、高斯模糊、自适应二值化、形态学操作"""
    if verbose:
        print("[INFO] 开始图像预处理...")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if verbose:
        print("[INFO] 已转换为灰度图")

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    if verbose:
        print("[INFO] 已应用高斯模糊")

    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )
    if verbose:
        print("[INFO] 已应用自适应阈值")

    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    if verbose:
        print("[INFO] 已应用开运算")

    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    if verbose:
        print("[INFO] 已应用闭运算")
        print("[INFO] 预处理完成")

    return closing


def decode_with_pyrxing(image_array, verbose=False):
    """
    使用 pyrxing 解码，兼容不同版本的属性命名。
    """
    results = []
    try:
        # 转换颜色空间 BGR -> RGB，并创建 PIL 图像
        rgb_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)

        barcodes = pyrxing.read_barcode(pil_img)
        if not isinstance(barcodes, list):
            barcodes = [barcodes] if barcodes else []

        for barcode in barcodes:
            if barcode is None:
                continue

            # 尝试获取解码内容：先尝试 data，再尝试 text，再尝试 content
            raw_data = None
            for attr in ['data', 'text', 'content', 'raw_bytes', 'decoded']:
                if hasattr(barcode, attr):
                    raw_data = getattr(barcode, attr)
                    break
            if raw_data is None:
                # 如果都没有，尝试直接转换为字符串
                raw_data = str(barcode)

            # 转换为字符串
            if isinstance(raw_data, bytes):
                try:
                    data = raw_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        data = raw_data.decode('gbk')
                    except UnicodeDecodeError:
                        data = raw_data.decode('latin-1', errors='replace')
            else:
                data = str(raw_data)

            # 获取格式：尝试 format 或 type
            fmt = None
            for attr in ['format', 'type']:
                if hasattr(barcode, attr):
                    fmt = getattr(barcode, attr)
                    break
            if fmt is None:
                fmt = "UNKNOWN"

            results.append((str(fmt), data))

            if verbose:
                print(f"[INFO] 发现码: {fmt} -> {data[:50]}{'...' if len(data)>50 else ''}")

    except Exception as e:
        if verbose:
            print(f"[ERROR] pyrxing 解码异常: {e}")
            # 打印对象信息帮助调试
            if 'barcode' in locals():
                print(f"[DEBUG] barcode 属性: {dir(barcode)}")
    return results


def decode_with_opencv(image_array, verbose=False):
    """OpenCV QR 码解码器（仅 QR）"""
    qr = cv2.QRCodeDetector()
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array
    data, points, _ = qr.detectAndDecode(gray)
    if data:
        return [("QR_CODE", data)]
    return []


def scan_image(image_path, preprocess=False, output_path=None, verbose=False):
    """扫描图片，返回解码结果列表"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")

    if verbose:
        print(f"[INFO] 加载图片: {image_path}")
        print(f"[INFO] 图像尺寸: {img.shape[1]}x{img.shape[0]}")

    # 预处理
    if preprocess:
        processed_img = preprocess_image(img, verbose)
        if output_path:
            cv2.imwrite(output_path, processed_img)
            if verbose:
                print(f"[INFO] 预处理图片已保存至: {output_path}")
        decode_img = processed_img
    else:
        decode_img = img

    # 解码
    results = []
    if PYRXING_AVAILABLE:
        if verbose:
            print("[INFO] 使用 pyrxing 解码器...")
        results = decode_with_pyrxing(decode_img, verbose)
        if results:
            if verbose:
                print(f"[INFO] pyrxing 检测到 {len(results)} 个码")
        else:
            if verbose:
                print("[INFO] pyrxing 未检测到码，尝试 OpenCV QR 备选...")
            results = decode_with_opencv(decode_img, verbose)
            if results and verbose:
                print("[INFO] OpenCV 备选解码成功")
    else:
        if verbose:
            print("[INFO] 使用 OpenCV 解码器（仅 QR 码）...")
        results = decode_with_opencv(decode_img, verbose)

    if not results and verbose:
        print("[WARNING] 未检测到任何二维码或条形码。")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="跨平台二维码/条形码扫描器（CTF专用）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例: python scan_code.py -i qrcode.png --preprocess -v"
    )
    parser.add_argument('-i', '--image', required=True, help='图片文件路径')
    parser.add_argument('-p', '--preprocess', action='store_true', help='启用增强预处理')
    parser.add_argument('-o', '--output', help='保存预处理后的图片路径（调试用）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')

    args = parser.parse_args()

    try:
        results = scan_image(
            args.image,
            preprocess=args.preprocess,
            output_path=args.output,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if results:
        print("\n========== 解码结果 ==========")
        for idx, (typ, data) in enumerate(results, 1):
            print(f"{idx}. 类型: {typ}")
            print(f"   内容: {data}")
            print()
    else:
        print("[ERROR] 未能解码出任何内容。")
        sys.exit(1)


if __name__ == "__main__":
    main()
