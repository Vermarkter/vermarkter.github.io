#!/usr/bin/env python
"""
Convert full-size images to WebP format (no resizing)
Maintain original dimensions for better detail visibility
"""

from PIL import Image
import os

def convert_to_webp_fullsize(input_path, quality=85):
    """
    Convert PNG to WebP without resizing
    """
    try:
        # Get original info
        original_size = os.path.getsize(input_path)
        original_size_mb = original_size / (1024 * 1024)

        # Create output path
        output_path = input_path.replace('-fullsize.png', '.webp')

        # Open image
        img = Image.open(input_path)
        original_width = img.width
        original_height = img.height

        # Save as WebP with high quality (no resizing)
        img.save(output_path, 'WEBP', quality=quality, method=6)

        # Get new size
        new_size = os.path.getsize(output_path)
        new_size_mb = new_size / (1024 * 1024)
        reduction = ((original_size - new_size) / original_size) * 100

        print(f"Converted: {os.path.basename(input_path)}")
        print(f"  Original PNG: {original_size_mb:.2f} MB")
        print(f"  New WebP: {new_size_mb:.2f} MB")
        print(f"  Reduction: {reduction:.1f}%")
        print(f"  Dimensions: {original_width}x{original_height} (unchanged)")
        print()

        return output_path
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return None

def main():
    """Convert all full-size portfolio images to WebP"""
    img_dir = "img"

    # Find all full-size PNG images
    portfolio_images = [
        os.path.join(img_dir, "portfolio-auto-fullsize.png"),
        os.path.join(img_dir, "portfolio-dashboard-fullsize.png"),
        os.path.join(img_dir, "portfolio-ecommerce-fullsize.png"),
        os.path.join(img_dir, "portfolio-salon-fullsize.png"),
    ]

    print("Converting full-size portfolio images to WebP...")
    print("=" * 60)

    converted_files = []
    for image_path in sorted(portfolio_images):
        if os.path.exists(image_path):
            webp_path = convert_to_webp_fullsize(image_path, quality=85)
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
