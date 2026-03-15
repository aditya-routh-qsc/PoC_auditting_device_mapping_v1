import os
import math
import glob
from PIL import Image, ImageDraw

# --- PAGE SPECIFICATIONS (A4 at 300 DPI) ---
PAGE_WIDTH = 2480
PAGE_HEIGHT = 3508
MARGIN = 100       # Starting point from the top-left edge
CELL_SIZE = 480    # The rigid size of the dotted-line box
QR_MAX_SIZE = 400  # The QR code will be scaled to fit comfortably inside the box

def draw_dashed_line(draw, start, end, fill="gray", width=3, dash_length=15):
    """Helper function to draw dashed lines for cutting guides."""
    x1, y1 = start
    x2, y2 = end
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0: return
    
    dashes = int(length / dash_length)
    for i in range(dashes):
        if i % 2 == 0:  
            sx = x1 + (x2 - x1) * i / dashes
            sy = y1 + (y2 - y1) * i / dashes
            ex = x1 + (x2 - x1) * (i + 1) / dashes
            ey = y1 + (y2 - y1) * (i + 1) / dashes
            draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)

def clear_processed_qrs(qr_list):
    """Deletes the individual QR code images to prevent system stress and disk bloat."""
    # print(f"\nCleaning up {len(qr_list)} individual source QR files...")
    for qr_file in qr_list:
        try:
            os.remove(qr_file)
        except OSError as e:
            print(f"Error deleting {qr_file}: {e}")
    # print("Cleanup complete. Source directory is clear.")

def create_qr_grid(input_dir="demo_qrs", output_dir="printable_sheets"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    qr_files = sorted(glob.glob(os.path.join(input_dir, "qr_device_*.png")), key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]))
    if not qr_files:
        print("No QR codes found in the input directory.")
        return

    total_qrs = len(qr_files)
    
    # 1. Calculate how many fixed cells fit on the page
    avail_w = PAGE_WIDTH - (2 * MARGIN)
    avail_h = PAGE_HEIGHT - (2 * MARGIN)
    
    cols = avail_w // CELL_SIZE
    rows = avail_h // CELL_SIZE
    qrs_per_page = cols * rows

    if qrs_per_page == 0:
        print("Error: The requested CELL_SIZE is too large for the page.")
        return

    total_pages = math.ceil(total_qrs / qrs_per_page)
    # print(f"Packing {total_qrs} QR codes into {total_pages} A4 sheet(s) (Cell-Centered)...")

    for page_num in range(total_pages):
        sheet = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
        draw = ImageDraw.Draw(sheet)
        
        start_idx = page_num * qrs_per_page
        end_idx = min(start_idx + qrs_per_page, total_qrs)
        page_qrs = qr_files[start_idx:end_idx]
        page_qrs_count = len(page_qrs)

        # Track grid usage to draw lines only where necessary
        max_row_used = -1
        max_col_used = -1

        for i, qr_path in enumerate(page_qrs):
            row = i // cols
            col = i % cols
            max_row_used = max(max_row_used, row)
            max_col_used = max(max_col_used, col)
            
            # Find the top-left corner of this specific cell
            cell_x = MARGIN + col * CELL_SIZE
            cell_y = MARGIN + row * CELL_SIZE
            
            with Image.open(qr_path) as img:
                # Resize the QR image
                img.thumbnail((QR_MAX_SIZE, QR_MAX_SIZE), Image.Resampling.LANCZOS)
                img_w, img_h = img.size
                
                # Center the image perfectly WITHIN the cell's coordinates
                paste_x = cell_x + (CELL_SIZE - img_w) // 2
                paste_y = cell_y + (CELL_SIZE - img_h) // 2
                
                sheet.paste(img, (paste_x, paste_y))

        # --- DRAW THE DOTTED BOXES ---
        # Draw Horizontal lines
        for r in range(max_row_used + 2):
            y_line = MARGIN + r * CELL_SIZE
            x_start = MARGIN
            # Draw line only as far as the columns used in this specific row
            cols_in_this_row = cols if r <= max_row_used else (page_qrs_count % cols or cols)
            if r == max_row_used + 1:
                x_end = MARGIN + cols_in_this_row * CELL_SIZE
            else:
                x_end = MARGIN + (max_col_used + 1) * CELL_SIZE
                
            draw_dashed_line(draw, (x_start, y_line), (x_end, y_line), fill="gray", width=3)

        # Draw Vertical lines
        for c in range(max_col_used + 2):
            x_line = MARGIN + c * CELL_SIZE
            y_start = MARGIN
            # Draw line only as deep as the rows used in this specific column
            rows_in_this_col = (max_row_used + 1) if (page_qrs_count % cols == 0 or c < page_qrs_count % cols) else max_row_used
            y_end = MARGIN + rows_in_this_col * CELL_SIZE
            
            if rows_in_this_col > 0:
                draw_dashed_line(draw, (x_line, y_start), (x_line, y_end), fill="gray", width=3)

        save_path = os.path.join(output_dir, f"A4_QR_Sheet_{page_num + 1}.png")
        sheet.save(save_path)
        # print(f"Saved: {save_path} (Grid footprint: {max_col_used + 1}x{max_row_used + 1})")

        clear_processed_qrs(page_qrs)

if __name__ == "__main__":
    create_qr_grid(input_dir="demo_qrs", output_dir="printable_sheets")