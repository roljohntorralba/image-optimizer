# Rol's Image Optimizer - WEBP/AVIF Converter

A GUI application built in Python that converts images to WEBP and/or AVIF formats with resizing and quality options.

## 📥 Download

### macOS Users
Download the latest version from the [Releases page](https://github.com/roljohntorralba/image-optimizer/releases/latest).

- **Direct Download**: [Rols-Image-Optimizer-v1.0.0-macOS.dmg](https://github.com/roljohntorralba/image-optimizer/releases/download/v1.0.0/Rols-Image-Optimizer-v1.0.0-macOS.dmg)

Simply download the DMG file, open it, and drag "Rol's Image Optimizer.app" to your Applications folder.

### Other Platforms
For Windows and Linux users, please install from source (see Installation section below).

## ✨ Features

- **Multiple Format Support**: Converts JPG, JPEG, PNG, BMP, TIFF, GIF, and WEBP images
- **Dual Output Formats**: Choose between WEBP, AVIF, or both
- **Smart Resizing**: 
  - Set maximum width and/or height
  - Maintains aspect ratio
  - Never enlarges images (only reduces size)
- **Quality Control**: Adjustable quality settings for both WEBP and AVIF outputs
- **Recursive Processing**: Processes images in subfolders while maintaining directory structure
- **Safe Operation**: Ignores existing "webp" and "avif" folders to prevent infinite loops
- **File Replacement**: Overwrites existing converted files when run again
- **Optimized Performance**: Fast processing with improved algorithms and progress tracking

## Installation

1. Make sure Python 3.7+ is installed on your system
2. Navigate to the project directory
3. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python image_optimizer.py
   ```

2. In the GUI:
   - **Source Folder**: Click "Browse" to select the folder containing your images
   - **Output Formats**: Choose WEBP, AVIF, or both
   - **Resize Settings**: 
     - Set maximum width and/or height (0 = no limit)
     - Images will be resized to fit within these dimensions while maintaining aspect ratio
   - **Quality Settings**: Adjust quality (1-100) for each format
   - Click "Start Optimization" to begin processing

3. The application will:
   - Create "webp" and/or "avif" folders in your source directory
   - Convert all supported images while maintaining the original folder structure
   - Show progress and logs in the application window

## Supported Image Formats

**Input formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- GIF (.gif)
- WEBP (.webp)

**Output formats:**
- WEBP (.webp)
- AVIF (.avif)

## Example Usage Scenarios

1. **Resize for web**: Set max width to 1920px and height to 1080px with quality 85
2. **Thumbnails**: Set max width to 512px and height to 512px with quality 75
3. **Width-only constraint**: Set width to 800px and height to 0 to resize based on width only

## Requirements

- Python 3.7+
- Pillow (PIL)
- pillow-avif-plugin (for AVIF support)
- tkinter (usually included with Python)

## Notes

- The application uses RGB color mode for output images
- RGBA images are converted by adding a white background
- Processing is done in a separate thread to keep the GUI responsive
- All operations preserve the original files - only copies are created in the output folders

## Troubleshooting

If you encounter issues with AVIF support:
1. Ensure `pillow-avif-plugin` is properly installed
2. Try updating Pillow to the latest version
3. On some systems, additional system libraries may be required for AVIF support
