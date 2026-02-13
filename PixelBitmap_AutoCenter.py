import json
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
from PIL import Image, ImageDraw, ImageFont

# ================= 布局与功能配置 =================
COLUMNS = 20         
CELL_W = 12          
CELL_H = 16          
LINE_W = 1           
FONT_SIZE = 12       

BG_COLOR = (240, 240, 240)    # 灰色背景
LINE_COLOR = (255, 255, 255)  # 白色格线
CHAR_COLOR = (0, 0, 0)        # 黑色文字

# 全局偏移（针对汉字）
X_OFFSET = 0         
Y_OFFSET = 1         

# --- 新增功能：非 CJK 字符（英/数/符号/希腊）特殊处理 ---
CENTER_NON_CJK = True      # 设为 True 则自动将英文字母/符号在 12px 格子内居中
NON_CJK_OFFSET_X = 2       # 如果上面设为 False，则固定往右偏移这么多像素
# ==================================================

def is_non_cjk(char):
    """
    判断字符是否为非 CJK 字符（例如英文、数字、希腊字母、基础符号等）。
    CJK 统一汉字和常用全角符号一般在 0x2E80 之后。
    """
    if not char: return False
    code = ord(char)
    # 0x0500 包含了基础拉丁、希腊语、西里尔字母等绝大部分非亚洲拼音文字
    return code < 0x0500 

def parse_char(char_field):
    if isinstance(char_field, str) and "0x" in char_field:
        try:
            return chr(int(char_field.split(" ")[0], 16))
        except:
            return char_field[0] if char_field else ""
    return str(char_field)

def get_paths():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        json_p = filedialog.askopenfilename(title="1. 选择 JSON", filetypes=[("JSON", "*.json")])
        if not json_p: return None
        font_p = filedialog.askopenfilename(title="2. 选择字体", filetypes=[("字体", "*.otf *.ttf *.bdf")])
        if not font_p: return None
        save_p = filedialog.asksaveasfilename(title="3. 保存 BMP", defaultextension=".bmp", filetypes=[("BMP", "*.bmp")])
        if not save_p: return None
        return json_p, font_p, save_p
    finally:
        root.destroy()

def main():
    paths = get_paths()
    if not paths: return
    json_p, font_p, save_p = paths

    try:
        with open(json_p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("错误", f"读取 JSON 失败:\n{e}")
        return

    try:
        font = ImageFont.truetype(font_p, FONT_SIZE)
    except Exception as e:
        messagebox.showerror("错误", f"加载字体失败:\n{e}")
        return

    chars = [parse_char(item.get("char", "")) for item in data]
    rows = math.ceil(len(chars) / COLUMNS)
    img_w = COLUMNS * (CELL_W + LINE_W) + LINE_W
    img_h = rows * (CELL_H + LINE_W) + LINE_W
    
    img = Image.new("RGB", (img_w, img_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    for c in range(COLUMNS + 1):
        x = c * (CELL_W + LINE_W)
        draw.line([(x, 0), (x, img_h)], fill=LINE_COLOR, width=1)
    for r in range(rows + 1):
        y = r * (CELL_H + LINE_W)
        draw.line([(0, y), (img_w, y)], fill=LINE_COLOR, width=1)

    print("正在渲染字符并自动优化间距...")
    for i, char in enumerate(chars):
        if not char or char.isspace(): continue
        
        col, row = i % COLUMNS, i // COLUMNS
        cell_x = col * (CELL_W + LINE_W) + LINE_W
        cell_y = row * (CELL_H + LINE_W) + LINE_W

        # --- 计算局部偏移 ---
        local_x_offset = X_OFFSET
        if is_non_cjk(char):
            if CENTER_NON_CJK:
                # 获取该字符的精确边界框 (left, top, right, bottom)
                bbox = font.getbbox(char)
                if bbox:
                    char_width = bbox[2] - bbox[0]
                    # 公式：(格子宽 - 字符实宽) / 2 - 字符自带左边距
                    # 这样能保证字母不论多窄，都绝对居中于 12px 的格子里
                    local_x_offset = (CELL_W - char_width) // 2 - bbox[0]
            else:
                local_x_offset += NON_CJK_OFFSET_X

        # --- 核心绘制逻辑 (使用 1-bit 临时画布完美解决杂色和基线问题) ---
        # 创建一个和格子一样大的黑白临时图片 (1-bit mode)
        temp_img = Image.new("1", (CELL_W, CELL_H), 0)
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 在临时图片上绘制白色文字 (1 代表纯白/有内容，0 代表纯黑/无内容)
        # 因为是 mode '1'，Pillow 会自动关闭抗锯齿，并且完美保留基线高度
        temp_draw.text((local_x_offset, Y_OFFSET), char, font=font, fill=1)
        
        # 将临时图片作为蒙版，把黑色贴到主画布上
        box = (cell_x, cell_y, cell_x + CELL_W, cell_y + CELL_H)
        img.paste(CHAR_COLOR, box, mask=temp_img)

    try:
        img.save(save_p)
        messagebox.showinfo("完成", f"位图生成成功！已自动居中英文字符。\n保存至: {save_p}")
    except Exception as e:
        messagebox.showerror("错误", f"保存失败:\n{e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("崩溃", f"运行时出错:\n{sys.exc_info()[0].__name__}: {e}")