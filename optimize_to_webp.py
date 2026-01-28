#!/usr/bin/env python
"""
Convert images to WebP format with optimization
"""

from PIL import Image
import os
import glob

def convert_to_webp(input_path, max_width=800, quality=80):
    """
    Convert PNG to WebP with optimization
    """
    try:
        # Get original info
        original_size = os.path.getsize(input_path)
        original_size_mb = original_size / (1024 * 1024)

        # Create output path
        output_path = input_path.replace('.png', '.webp')

        # Open and resize image
        img = Image.open(input_path)

        # Resize if wider than max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save as WebP with high quality
        img.save(output_path, 'WEBP', quality=quality, method=6)

        # Get new size
        new_size = os.path.getsize(output_path)
        new_size_mb = new_size / (1024 * 1024)
        reduction = ((original_size - new_size) / original_size) * 100

        print(f"Converted: {os.path.basename(input_path)}")
        print(f"  Original PNG: {original_size_mb:.2f} MB")
        print(f"  New WebP: {new_size_mb:.2f} MB")
        print(f"  Reduction: {reduction:.1f}%")
        print(f"  Dimensions: {img.width}x{img.height}")
        print()

        return output_path
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return None

def main():
    """Convert all portfolio images to WebP"""
    img_dir = "img"

    if not os.path.exists(img_dir):
        print(f"Error: {img_dir} directory not found")
        return

    # Find all portfolio PNG images
    portfolio_images = glob.glob(os.path.join(img_dir, "portfolio-*.png"))

    if not portfolio_images:
        print("No portfolio images found")
        return

    print("Converting portfolio images to WebP...")
    print("=" * 60)

    converted_files = []
    for image_path in sorted(portfolio_images):
        webp_path = convert_to_webp(image_path, max_width=800, quality=85)
        if webp_path:
            converted_files.append(webp_path)

    print("=" * 60)
    print(f"Conversion complete! Created {len(converted_files)} WebP files")
    print()
    print("WebP files created:")
    for f in converted_files:
        size = os.path.getsize(f) / (1024 * 1024)
        print(f"  - {os.path.basename(f)}: {size:.2f} MB")

if __name__ == "__main__":
    main()
