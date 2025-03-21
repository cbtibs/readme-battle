#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

TXT_FILE = "battle_map.txt"
IMG_FILE = "battle_map.png"

def txt_to_img(txt, font_path=None, font_size=16, padding=10, bg_color="white", fg_color="black"):
    # Split the text into lines.
    lines = txt.splitlines()
    
    # Use a monospaced font. Try using DejaVuSansMono if no font_path is provided.
    if font_path is None:
        default_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        if os.path.exists(default_font_path):
            font = ImageFont.truetype(default_font_path, font_size)
        else:
            font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)

    def get_text_size(text):
        # Using getbbox() to get the dimensions.
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    # Calculate the maximum line width and the total height.
    max_line_width = 0
    total_height = 0
    line_heights = []
    for line in lines:
        w, h = get_text_size(line)
        max_line_width = max(max_line_width, w)
        line_heights.append(h)
        total_height += h

    img_width = max_line_width + 2 * padding
    img_height = total_height + 2 * padding

    # Create the image.
    image = Image.new("RGB", (img_width, img_height), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Draw each line.
    y = padding
    for i, line in enumerate(lines):
        draw.text((padding, y), line, font=font, fill=fg_color)
        y += line_heights[i]

    return image

def main():
    if not os.path.exists(TXT_FILE):
        print(f"{TXT_FILE} does not exist!")
        return
    with open(TXT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    image = txt_to_img(content, font_size=16, padding=10, bg_color="white", fg_color="black")
    image.save(IMG_FILE)
    print(f"Image saved as {IMG_FILE}")

if __name__ == "__main__":
    main()
