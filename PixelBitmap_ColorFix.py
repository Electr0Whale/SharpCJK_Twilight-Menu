import sys
from PIL import Image

def color_distance(c1, c2):
    """计算两个RGB颜色之间的曼哈顿距离"""
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

def process_bmp(input_path, output_path, threshold=30):
    """
    处理BMP图像，只保留黑、浅灰、白三种颜色。
    :param input_path: 输入BMP文件路径
    :param output_path: 输出BMP文件路径
    :param threshold: 颜色接近阈值（曼哈顿距离）
    """
    # 打开图像并转换为RGB模式（确保三通道）
    img = Image.open(input_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # 定义目标颜色
    BLACK = (0, 0, 0)
    GRAY = (240, 240, 240)   # f0f0f0
    WHITE = (255, 255, 255)

    # 遍历每个像素
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            # 计算与黑色的距离
            if color_distance((r, g, b), BLACK) < threshold:
                pixels[x, y] = BLACK
            # 否则计算与灰色的距离
            elif color_distance((r, g, b), GRAY) < threshold:
                pixels[x, y] = GRAY
            # 其余像素设为白色
            else:
                pixels[x, y] = WHITE

    # 保存结果
    img.save(output_path)
    print(f"处理完成，结果已保存至：{output_path}")

if __name__ == "__main__":
    # 简单命令行参数处理
    if len(sys.argv) < 3:
        print("用法：python script.py 输入图片.bmp 输出图片.bmp [阈值]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    thr = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    process_bmp(input_file, output_file, thr)