import os
from PIL import Image, ImageDraw, ImageOps

def apply_border(image_path, corner_radius=24, target_width=800):
    """Resizes image to target_width and applies smooth anti-aliased corners."""
    try:
        img = Image.open(image_path).convert("RGBA")
        
        # Calculate new size while maintaining aspect ratio
        if img.width > target_width:
            aspect_ratio = img.height / img.width
            new_size = (target_width, int(target_width * aspect_ratio))
            # Use high-quality LANCZOS for resizing
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            new_size = img.size
            
        # Create a high-res mask for anti-aliasing (4x scale)
        scale = 4
        mask_size = (new_size[0] * scale, new_size[1] * scale)
        mask = Image.new('L', mask_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), mask_size], corner_radius * scale, fill=255)
        
        # Downsample mask back to original size for smooth edges
        mask = mask.resize(new_size, Image.Resampling.LANCZOS)
        
        # Apply mask
        output = Image.new("RGBA", new_size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # Save as PNG with optimization
        output.save(image_path, "PNG", optimize=True)
        print(f"✅ Optimized and smoothed {os.path.basename(image_path)} ({new_size[0]}x{new_size[1]})")
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
