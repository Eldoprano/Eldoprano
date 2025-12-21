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
