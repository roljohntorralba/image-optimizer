#!/usr/bin/env python3
"""
Test script to create sample images for testing the Image Optimizer
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

def create_test_images():
    """Create sample test images"""
    # Create test directory structure
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    # Create a subdirectory
    sub_dir = test_dir / "subfolder"
    sub_dir.mkdir(exist_ok=True)
    
    # Create sample images with different sizes and formats
    test_images = [
        ("sample1.jpg", (800, 600), "RGB", "red"),
        ("sample2.png", (1200, 800), "RGBA", "blue"),
        ("sample3.bmp", (400, 300), "RGB", "green"),
        ("subfolder/sample4.jpg", (1920, 1080), "RGB", "yellow"),
        ("subfolder/sample5.png", (500, 500), "RGBA", "purple"),
    ]
    
    for filename, size, mode, color in test_images:
        file_path = test_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create image
        img = Image.new(mode, size, color)
        draw = ImageDraw.Draw(img)
        
        # Add some text to make it interesting
        text = f"{filename}\n{size[0]}x{size[1]}\n{mode}"
        draw.text((50, 50), text, fill="white" if color != "yellow" else "black")
        
        # Save image
        img.save(file_path)
        print(f"Created: {file_path}")
    
    print(f"\nTest images created in '{test_dir}' directory")
    print("You can now use these images to test the Image Optimizer!")

if __name__ == "__main__":
    create_test_images()
