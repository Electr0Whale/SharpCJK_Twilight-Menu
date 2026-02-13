import json
import math
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
from PIL import Image, ImageDraw, ImageFont

# ================= 布局与功能配置 =================
COLUMNS = 20         
CELL_W = 12          # 你当前的参数
CELL_H = 16          # 你当前的参数
LINE_W = 1           
FONT_SIZE = 12       # 你当前的参数

BG_COLOR = (240, 240, 240)    # 灰色背景
LINE_COLOR = (255, 255, 255)  # 白色格线
CHAR_COLOR = (0, 0, 0)        # 黑色文字

# --- 主字体偏移 (Primary Font) ---
X_OFFSET = 0         
Y_OFFSET = 1         

# --- 副字体专属偏移 (Secondary Font) ---
# 当主字体缺字切换到副字体时，使用下面这两个参数进行对齐微调
X_OFFSET_SEC = 0     
Y_OFFSET_SEC = 0     

# --- 非 CJK 字符专属偏移 ---
NON_CJK_OFFSET_X = 0 # 你当前的参数
# ==================================================

def is_non_cjk(char):
    if not char: return False
    return ord(char) < 0x0500 

def parse_char(char_field):
    if isinstance(char_field, str) and "0x" in char_field:
        try:
            return chr(int(char_field.split(" ")[0], 16))
        except:
            return char_field[0] if char_field else ""
    return str(char_field)

def get_char_mask_info(font, char):
    """安全获取字符蒙版数据"""
    mask = font.getmask(char, mode='1')
    try:
        return list(mask), mask.size
    except:
        return str(mask), mask.size

def get_paths():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        json_p = filedialog.askopenfilename(title="1. 选择 JSON", filetypes=[("JSON", "*.json")])
        if not json_p: return None
        font1_p = filedialog.askopenfilename(title="2. 选择【主字体】", filetypes=[("字体", "*.otf *.ttf *.bdf")])
        if not font1_p: return None
        font2_p = filedialog.askopenfilename(title="3. 选择【副字体】(取消则仅用单字体)", filetypes=[("字体", "*.otf *.ttf *.bdf")])
        save_p = filedialog.asksaveasfilename(title="4. 保存 BMP", defaultextension=".bmp", filetypes=[("BMP", "*.bmp")])
        if not save_p: return None
        return json_p, font1_p, font2_p, save_p
    finally:
        root.destroy()

def main():
    paths = get_paths()
    if not paths: return
    json_p, font1_p, font2_p, save_p = paths

    try:
        with open(json_p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("错误", f"读取 JSON 失败:\n{e}")
        return

    try:
        font_primary = ImageFont.truetype(font1_p, FONT_SIZE)
        primary_missing_sig = get_char_mask_info(font_primary, chr(0xFFFF))
        
        font_secondary = None
        if font2_p:
            font_secondary = ImageFont.truetype(font2_p, FONT_SIZE)
            print("✅ 双字体独立偏移模式已激活")
    except Exception as e:
        messagebox.showerror("加载字体失败", f"错误详情: {e}")
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

    print("开始根据主副字体偏移设置渲染...")
    fallback_count = 0

    for i, char in enumerate(chars):
        if not char or char.isspace(): continue
        
        col, row = i % COLUMNS, i // COLUMNS
        cell_x = col * (CELL_W + LINE_W) + LINE_W
        cell_y = row * (CELL_H + LINE_W) + LINE_W

        # 判断使用哪个字体及其对应的偏移
        if font_secondary and get_char_mask_info(font_primary, char) == primary_missing_sig:
            target_font = font_secondary
            current_x_off = X_OFFSET_SEC
            current_y_off = Y_OFFSET_SEC
            fallback_count += 1
        else:
            target_font = font_primary
            current_x_off = X_OFFSET
            current_y_off = Y_OFFSET

        # 如果是非CJK字符，叠加额外的横向偏移
        if is_non_cjk(char):
            current_x_off += NON_CJK_OFFSET_X

        # 渲染到临时 1-bit 画布
        temp_img = Image.new("1", (CELL_W, CELL_H), 0)
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((current_x_off, current_y_off), char, font=target_font, fill=1)
        
        # 粘贴回主图
        box = (cell_x, cell_y, cell_x + CELL_W, cell_y + CELL_H)
        img.paste(CHAR_COLOR, box, mask=temp_img)

    try:
        img.save(save_p)
        messagebox.showinfo("完成", f"生成成功！\n主字体偏移: ({X_OFFSET}, {Y_OFFSET})\n副字体偏移: ({X_OFFSET_SEC}, {Y_OFFSET_SEC})\n兜底次数: {fallback_count}")
    except Exception as e:
        messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("运行错误", str(e))