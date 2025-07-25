"""
创建应用图标
"""
import sys
import os

try:
    from PIL import Image, ImageDraw
    
    def create_simple_icon(output_path, size=256, bg_color=(0, 120, 212), text="LC"):
        # 创建新图像
        img = Image.new('RGB', (size, size), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", size=int(size*0.5))
        except Exception:
            font = None
        
        # 绘制文本
        if font:
            # 新版PIL使用font.getbbox或font.getsize代替draw.textsize
            try:
                w, h = font.getsize(text)
            except AttributeError:
                # 更新版本的PIL使用getbbox
                bbox = font.getbbox(text)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        else:
            w, h = size//2, size//2
            
        draw.text(
            ((size-w)//2, (size-h)//2), 
            text, 
            fill="white", 
            font=font
        )
        
        # 保存为.ico文件
        if not output_path.endswith('.ico'):
            output_path += '.ico'
            
        img.save(output_path, format='ICO')
        print(f"图标已创建: {output_path}")
        return True
    
    if __name__ == "__main__":
        output = "icon.ico"
        if len(sys.argv) > 1:
            output = sys.argv[1]
        
        create_simple_icon(output)
        
except ImportError:
    print("需要安装Pillow库才能创建图标: pip install pillow")
    
    # 创建一个空的图标文件占位符
    if __name__ == "__main__":
        output = "icon.ico" if len(sys.argv) <= 1 else sys.argv[1]
        with open(output, 'wb') as f:
            f.write(b'')  # 写入空文件作为占位符
        print(f"创建了空图标文件: {output}")
