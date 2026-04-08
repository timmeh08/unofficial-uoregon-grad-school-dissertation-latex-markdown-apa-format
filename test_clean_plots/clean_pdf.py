import os
import glob
import fitz  # PyMuPDF


def process_pdf(input_path, output_path, target_text="ATLAS", dpi=300):
    doc = fitz.open(input_path)
    output_doc = fitz.open()
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    try:
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)

            # 1. Search for the text string
            text_instances = page.search_for(target_text)

            # 2. Add a white annotation rectangle over each match.
            # This avoids text reflow while handling rotated page coordinates.
            for inst in text_instances:
                pad = 0.5
                box = fitz.Rect(
                    inst.x0 - pad,
                    inst.y0 - pad,
                    inst.x1 + pad,
                    inst.y1 + pad,
                )
                annot = page.add_rect_annot(box)
                annot.set_colors(stroke=(1, 1, 1), fill=(1, 1, 1))
                annot.set_border(width=0)
                annot.update(opacity=1)

            # Burn annotations into the page so LaTeX includes the white mask.
            pixmap = page.get_pixmap(matrix=matrix, annots=True, alpha=False)
            output_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
            output_page.insert_image(output_page.rect, pixmap=pixmap)

        output_doc.save(output_path, deflate=True)
    finally:
        output_doc.close()
        doc.close()

    print(f"Processed PDF: {output_path}")

source_folder = '../images/dark_photon/vertexing/'
output_folder = '../images/clean_vertexing/'

# Make output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Find all PDFs
pdf_files = [
    path for path in glob.glob(os.path.join(source_folder, '*.pdf'))
    if not os.path.basename(path).startswith('clean_')
]

for pdf_path in pdf_files:
    filename = os.path.basename(pdf_path)
    clean_filename = f"clean_{filename}"
    output_path = os.path.join(output_folder, clean_filename)
    
    # Process each PDF using the function defined above
    process_pdf(pdf_path, output_path)

print("Batch processing complete!")

# Example usage for one file
# process_pdf('plot_123.pdf', 'plot_123_clean.pdf')