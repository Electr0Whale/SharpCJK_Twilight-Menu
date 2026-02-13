## TWiLight Menu++ CJK 锐利字库制作工具

本项目旨在为 **TWiLight Menu++** 制作清晰、锐利且支持 CJK（中日韩）字符的点阵字体。TWiLight Menu++ 默认使用的字体在 NDS 屏幕上往往显得模糊，通过本项目提供的流程，你可以实现 1:1 像素对齐的精美显示效果。

> [!IMPORTANT]
> 本项目中的所有 Python 脚本均由 **Gemini** 协作生成，旨在通过 AI 辅助解决复古游戏设备的汉化排版问题。

### 📂 准备工作

1. **定位默认字体**：
* TWiLight Menu++ 默认字体路径：`sd:/_nds/TWiLightMenu/extras/fonts/Default/`。
* 你需要其中的 `small.nftr` 和 `large.nftr`（本项目 `default` 文件夹中已提供副本）。


2. **生成字符表**：
* 访问 [nftr-editor | pk11.us](https://www.google.com/search?q=https://pk11.us/nftr-editor) 上传 `.nftr` 文件，获取对应的 **JSON 字符顺序表**。


3. **下载必要工具**：
* 下载 [NFTRedit | GBAtemp.net](https://www.google.com/search?q=https://gbatemp.net/download/nftredit.36109/) 用于将图片导入到字体文件中。



### 🛠️ 制作流程

1. **运行脚本**：根据需求运行下方的 Python 脚本，将 JSON 字符表和字体文件转换为 BMP 图片。
2. **导入 Tiles**：使用 **NFTRedit** 打开原始 `nftr`，选择 `Import Tiles` -> `From Image` 导入生成的 BMP。
3. **预览与微调**：在 NFTRedit 中查看预览，必要时进行手动像素修正。
4. **保存导出**：将导出的 `nftr` 存放在：`sd:/_nds/TWiLightMenu/extras/fonts/[自定义名称]/`。
5. **应用设置**：在 TWiLight Menu++ 的设置菜单中更换为你制作的字体。

### 📜 脚本功能说明 (Python Scripts)

| 脚本文件名 | 核心功能说明 |
| --- | --- |
| **`NFTR_Generator_Classic.py`** | 原始版本，支持基础的字符 XY 偏移方案。 |
| **`NFTR_Generator_Centered.py`** | 自动居中版，针对非 CJK 字符实现格内自动水平居中。 |
| **`NFTR_Generator_DualFont.py`** | **(推荐)** 增加主副字体选择，主字体缺字时自动调用副字体。 |
| **`NFTR_Generator_DualOffset.py`** | 改进版，支持为主副字体分别设置不同的 XY 偏移值。 |
| **`NFTR_Bitmap_Fixer.py`** | 独立工具，用于修复抗锯齿导致的图片偏色（通常无需使用）。 |

### ⚙️ 参数配置建议

* **单元格大小 (Cell Size)**：
* Small: `12 * 16`
* Large: `14 * 17`


* **字体大小 (Font Size)**：根据所选像素字体的原生尺寸填写（如 12 或 13）。
* **XY 偏移 (XY Offset)**：用于对齐基线。**正值**使字符向**右/下**移动，**负值**向**左/上**移动。双击脚本后按提示选择文件即可。

### ⚖️ 开源协议与鸣谢

本项目附带了以下开源字体的 BDF 文件：

* **文泉驿点阵宋体 (Habitat: BitmapSong)**：由 pcf2bdf 转换，遵循 **GPLv2** 协议。
* **Fusion Pixel Font**：来自 [TakWolf/fusion-pixel-font](https://www.google.com/search?q=https://github.com/TakWolf/fusion-pixel-font)，遵循 **SIL Open Font License v1.1**。

**Release 说明**：

* `wqy.7z`: 仅包含文泉驿点阵宋体制作的字库。
* `wqyfusion.7z`: 以文泉驿为主，Fusion Pixel 为补全的复合字库。
