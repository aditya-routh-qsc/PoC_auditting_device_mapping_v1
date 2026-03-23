import os
import glob
from PIL import Image

def clear_processed_sheets(sheet_list):
    """Deletes the individual A4 PNG sheets after they are safely in the PDF."""
    # print(f"\nCleaning up {len(sheet_list)} intermediate A4 PNG sheets...")
    for sheet_file in sheet_list:
        try:
            os.remove(sheet_file)
        except OSError as e:
            print(f"Error deleting {sheet_file}: {e}")
    print("Cleanup complete. The printable_sheets directory is clear.")

def convert_sheets_to_pdf(input_dir="printable_sheets", output_filename="qr-codes-qsys-audit.pdf"):
    # 1. Gather all the generated A4 PNG sheets and sort them
    sheet_files = sorted(glob.glob(os.path.join(input_dir, "A4_QR_Sheet_*.png")))
    
    if not sheet_files:
        print(f"No A4 sheets found in '{input_dir}'. Please run the grid generator first.")
        return

    # print(f"Found {len(sheet_files)} sheet(s). Compiling into a single PDF...")

    image_list = []
    
    # 2. Open the base image
    base_image = Image.open(sheet_files[0]).convert("RGB")

    # 3. Append remaining pages
    for file in sheet_files[1:]:
        img = Image.open(file).convert("RGB")
        image_list.append(img)

    # 4. Save the PDF
    base_image.save(
        output_filename,
        "PDF",
        resolution=300.0,
        save_all=True,
        append_images=image_list
    )
    
    # print(f"Success! Your print-ready file is saved as: {output_filename}")
    
    # 5. Call the cleanup function now that the PDF is safely saved
    clear_processed_sheets(sheet_files)

if __name__ == "__main__":
    convert_sheets_to_pdf()