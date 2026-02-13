import json
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
from PIL import Image, ImageDraw, ImageFont

# ================= 布局与功能配置 =================
COLUMNS = 20         
CELL_W = 10          
CELL_H = 12          
LINE_W = 1           
FONT_SIZE = 10       

BG_COLOR = (240, 240, 240)    # 灰色背景
LINE_COLOR = (255, 255, 255)  # 白色格线
CHAR_COLOR = (0, 0, 0)        # 黑色文字

# 全局偏移（针对所有字符的基础偏移）
X_OFFSET = 0         
Y_OFFSET = 1         

# --- 非 CJK 字符（英文字母、数字、符号等）专属偏移 ---
# 设为 1 或 2，能在字母左侧强制空出像素，解决 ic, ju 等粘连问题
NON_CJK_OFFSET_X = 0       
# ==================================================

def is_non_cjk(char):
    """
    判断是否为非中日韩字符（基础拉丁字母、符号、希腊字母等）。
    返回 True 则应用专属偏移量。
    """
    if not char: return False
    return ord(char) < 0x0500 

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

    # 画背景网格
    for c in range(COLUMNS + 1):
        x = c * (CELL_W + LINE_W)
        draw.line([(x, 0), (x, img_h)], fill=LINE_COLOR, width=1)
    for r in range(rows + 1):
        y = r * (CELL_H + LINE_W)
        draw.line([(0, y), (img_w, y)], fill=LINE_COLOR, width=1)

    print("正在渲染字符...")
    for i, char in enumerate(chars):
        if not char or char.isspace(): continue
        
        col, row = i % COLUMNS, i // COLUMNS
        cell_x = col * (CELL_W + LINE_W) + LINE_W
        cell_y = row * (CELL_H + LINE_W) + LINE_W

        # --- 简单粗暴的固定偏移 ---
        local_x_offset = X_OFFSET
        if is_non_cjk(char):
            local_x_offset += NON_CJK_OFFSET_X  # 只有非汉字会向右推

        # 创建 12x16 的纯黑白临时画布，保证不会越界，且没有灰阶杂色
        temp_img = Image.new("1", (CELL_W, CELL_H), 0)
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 在临时画布上画白字
        temp_draw.text((local_x_offset, Y_OFFSET), char, font=font, fill=1)
        
        # 贴回主图
        box = (cell_x, cell_y, cell_x + CELL_W, cell_y + CELL_H)
        img.paste(CHAR_COLOR, box, mask=temp_img)

    try:
        img.save(save_p)
        messagebox.showinfo("完成", f"位图生成成功！\n英文字符已向右偏移 {NON_CJK_OFFSET_X} 像素。\n保存至: {save_p}")
    except Exception as e:
        messagebox.showerror("错误", f"保存失败:\n{e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("崩溃", f"运行时出错:\n{sys.exc_info()[0].__name__}: {e}")