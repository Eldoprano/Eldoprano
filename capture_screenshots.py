import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageOps
import os

projects = [
    {"name": "Photo Splat Gallery", "url": "https://eldoprano.github.io/photo-splat-gallery/", "slug": "photo-splat"},
    {"name": "Tokyo Sticker DB", "url": "https://eldoprano.github.io/tokyo-sticker-db/", "slug": "tokyo-stickers"},
    {"name": "Learn Kana", "url": "https://eldoprano.github.io/learn-kana/", "slug": "learn-kana"},
    {"name": "Lenticular Generator", "url": "https://eldoprano.github.io/Lenticular-Postcard-Generator/", "slug": "lenticular"},
    {"name": "Peru Driving Test", "url": "https://eldoprano.github.io/test-drive-peru-A1/", "slug": "peru-driving"},
    {"name": "3D Texture Compressor", "url": "https://eldoprano.github.io/3d-texture-compressor/", "slug": "texture-compressor"},
    {"name": "3D Gen for Print", "url": "https://github.com/Eldoprano/Project-3D-Gen-4-Print/", "slug": "3d-gen-print"},
    {"name": "WiFi Fingerprinting", "url": "https://github.com/Eldoprano/probe_request_fingerprinting", "slug": "wifi-fingerprint"},
    {"name": "Data Structures Gist", "url": "https://gist.github.com/Eldoprano/0c09fd33b9dfd3e6b8d396159b4a9bfd", "slug": "ds-gist"}
]

OUTPUT_DIR = "assets/screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def apply_border(image_path, corner_radius=24, target_width=800):
    """Resizes image to target_width and applies anti-aliased rounded corners."""
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

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 800, "height": 600},
            color_scheme='dark'
        )
        
        for project in projects:
            print(f"Capturing {project['name']}...")
            try:
                await page.goto(project['url'], wait_until="networkidle", timeout=60000)
                
                # Specific handling for heavier sites
                if project['slug'] == 'photo-splat':
                    print("Waiting extra time for Photo Splat to initialize...")
                    await page.wait_for_timeout(10000)
                else:
                    await page.wait_for_timeout(2000)
                
                raw_path = f"{OUTPUT_DIR}/{project['slug']}_raw.png"
                final_path = f"{OUTPUT_DIR}/{project['slug']}.png"
                
                await page.screenshot(path=raw_path)
                
                # Use the improved border logic
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(raw_path, final_path)
                apply_border(final_path)
                
            except Exception as e:
                print(f"Failed to capture {project['name']}: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
