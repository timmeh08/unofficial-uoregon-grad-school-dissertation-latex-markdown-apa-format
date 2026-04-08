import os
import glob
import shutil
from PIL import Image, ImageDraw
import pytesseract


def configure_tesseract_binary():
    # Prefer PATH, then fall back to common macOS Homebrew locations.
    tesseract_cmd = shutil.which("tesseract")
    if not tesseract_cmd:
        for candidate in ("/usr/local/bin/tesseract", "/opt/homebrew/bin/tesseract"):
            if os.path.exists(candidate):
                tesseract_cmd = candidate
                break

    if not tesseract_cmd:
        raise RuntimeError(
            "Tesseract binary not found. Install it with: brew install tesseract"
        )

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def process_png(input_path, output_path, target_text="ATLAS"):
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    
    # 1. Get OCR data
    # This identifies words and their bounding boxes
    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    # 2. Iterate through detected text to find "ATLAS"
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        detected_text = d['text'][i].upper() # Check case-insensitive
        
        if detected_text == target_text.upper():
            # Get bounding box coordinates
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # 3. Draw a white box over the text
            # Define coordinates (x0, y0, x1, y1)
            # Make the box slightly larger to ensure coverage
            padding = 2
            draw.rectangle([x - padding, y - padding, x + w + padding, y + h + padding], fill="white")
            
    img.save(output_path)
    print(f"Processed PNG: {output_path}")

source_folder = '../images/dark_photon_paper/'
output_folder = '../images/clean_dark_photon_paper/'

configure_tesseract_binary()

# Make output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Find all PNGs
png_files = [
    path for path in glob.glob(os.path.join(source_folder, '*.png'))
    if not os.path.basename(path).startswith('clean_')
]

for png_path in png_files:
    filename = os.path.basename(png_path)
    clean_filename = f"clean_{filename}"
    output_path = os.path.join(output_folder, clean_filename)
    
    # Process each PNG using the function defined above
    process_png(png_path, output_path)

print("Batch processing complete!")


# Example usage
# process_png('plot_123.png', 'plot_123_clean.png')