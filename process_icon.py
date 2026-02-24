from PIL import Image, ImageDraw, ImageChops
import os

img_path = r'c:\Users\elchanan yehuda\Documents\atomic-downloader\static\images\logo.png'
ico_path = r'c:\Users\elchanan yehuda\Documents\atomic-downloader\static\images\logo.ico'

def process_icon():
    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found.")
        return

    print("Opening image...")
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # Calculate radius (e.g., 22% of size for a nice "squircle" or rounded rect look)
    # iOS icon style is roughly 22%
    radius = int(min(w, h) * 0.22)
    
    print(f"Applying rounded corners (radius={radius})...")
    
    # Create mask: black (0) = transparent, white (255) = opaque
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw filled rounded rectangle on mask
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    
    # Combine with existing alpha if present
    if 'A' in img.getbands():
        alpha = img.split()[-1]
        final_alpha = ImageChops.multiply(alpha, mask)
        img.putalpha(final_alpha)
    else:
        img.putalpha(mask)

    # Save as ICO with multiple sizes for best scaling
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Success! Rounded icon saved to: {ico_path}")

if __name__ == "__main__":
    process_icon()
