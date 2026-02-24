from PIL import Image
import os

img_path = r'c:\Users\elchanan yehuda\Documents\atomic-downloader\static\images\logo.png'
ico_path = r'c:\Users\elchanan yehuda\Documents\atomic-downloader\static\images\logo.ico'

if os.path.exists(img_path):
    img = Image.open(img_path)
    img.save(ico_path, format='ICO', sizes=[(256, 256)])
    print(f"Converted {img_path} to {ico_path}")
else:
    print(f"Image not found at {img_path}")
