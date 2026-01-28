#!/usr/bin/env python
"""
Image optimization script for portfolio images
Reduces file size while maintaining acceptable quality
"""

from PIL import Image
import os
import glob

def optimize_image(input_path, output_path, max_width=1200, quality=80):
    """
    Optimize an image by:
    1. Reducing dimensions to max_width
    2. Reducing quality/compression
    3. Converting to optimized format
    """
    try:
        # Open image
        img = Image.open(input_path)

        # Get original info
        original_size = os.path.getsize(input_path)
        original_size_mb = original_size / (1024 * 1024)

        # Resize if wider than max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Convert RGBA to RGB if necessary (for better PNG compression)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Save optimized image
        img.save(output_path, 'PNG', optimize=True, quality=quality)

        # Get new size
        new_size = os.path.getsize(output_path)
        new_size_mb = new_size / (1024 * 1024)
        reduction = ((original_size - new_size) / original_size) * 100

        print(f"Optimized: {os.path.basename(input_path)}")
        print(f"  Original: {original_size_mb:.2f} MB")
        print(f"  Optimized: {new_size_mb:.2f} MB")
        print(f"  Reduction: {reduction:.1f}%")
        print()

        return True
    except Exception as e:
        print(f"Error optimizing {input_path}: {e}")
        return False

def main():
    """Optimize all portfolio images"""
    img_dir = "img"

    if not os.path.exists(img_dir):
        print(f"Error: {img_dir} directory not found")
        return

    # Find all portfolio PNG images
    portfolio_images = glob.glob(os.path.join(img_dir, "portfolio-*.png"))

    if not portfolio_images:
        print("No portfolio images found")
        return

    print("Starting image optimization...")
    print("=" * 50)

    for image_path in sorted(portfolio_images):
        optimize_image(image_path, image_path, max_width=1200, quality=85)

    print("=" * 50)
    print("Optimization complete!")

if __name__ == "__main__":
    main()
