import os
from PIL import Image, ImageDraw, ImageOps

def apply_border(image_path, corner_radius=20, border_width=2, border_color=(255, 255, 255, 60)):
    """Applies rounded corners and a subtle border stroke to an image."""
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Create mask for rounded corners
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], corner_radius, fill=255)
        
        # Apply mask
        output = ImageOps.fit(img, img.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        
        # Add a subtle border stroke
        if border_width > 0:
            stroke_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
            stroke_draw = ImageDraw.Draw(stroke_img)
            stroke_draw.rounded_rectangle(
                [(0, 0), (img.size[0]-1, img.size[1]-1)], 
                corner_radius, 
                outline=border_color, 
                width=border_width
            )
            output = Image.alpha_composite(output, stroke_img)
        
        output.save(image_path, "PNG")
        print(f"✅ Processed {os.path.basename(image_path)}")
    except Exception as e:
        print(f"❌ Failed to process {image_path}: {e}")

if __name__ == "__main__":
    SCREENSHOTS_DIR = "assets/screenshots"
    
    if not os.path.exists(SCREENSHOTS_DIR):
        print(f"Error: Directory {SCREENSHOTS_DIR} not found.")
    else:
        print(f"Applying borders to images in {SCREENSHOTS_DIR}...")
        for filename in os.listdir(SCREENSHOTS_DIR):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                if "_raw" in filename: continue
                apply_border(os.path.join(SCREENSHOTS_DIR, filename))
        print("Done!")
