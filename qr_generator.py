from aiohttp.web_routedef import get
import qrcode
import os
from PIL import Image, ImageDraw, ImageFont
from get_sys_net_info import get_local_ip, get_port_number, get_local_hostname


# --- CONFIGURATION ---
LAPTOP_IP = get_local_ip() 
PORT = get_port_number()
OUTPUT_DIR = "demo_qrs"
HOST_NAME = get_local_hostname()

HOST = HOST_NAME

def create_qr_codes(start_id: int, end_id: int = -1, skip_by: int = 1):
    if end_id == -1: 
        end_id = start_id
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Detected Host: {HOST}")
    print("Generating QR codes...")

    for qr_id in range(start_id, end_id + 1, skip_by):
        url = f"http://{HOST}:{PORT}/?qr_id={qr_id}"
        
        # 1. Generate the QR code with a SMALLER border (default is 4, we use 1)
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        
        qr_width, qr_height = qr_img.size
        
        # 2. Reduce the extra canvas space at the bottom (changed from 50 to 35)
        text_space = 35 
        new_img = Image.new("RGB", (qr_width, qr_height + text_space), "white")
        
        # 3. Paste the QR code into the top of the new image
        new_img.paste(qr_img, (0, 0))
        
        # 4. Initialize drawing to add text
        draw = ImageDraw.Draw(new_img)
        
        try:
            # You can also change the '24' here to make the text smaller/larger
            font = ImageFont.truetype("arial.ttf", 34)
        except IOError:
            font = ImageFont.load_default()
        
        text = f"{qr_id}"
        
        # Get text bounding box to calculate centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (qr_width - text_width) // 2
        # Adjusted the math slightly to center the text perfectly in the new smaller space
        y = qr_height + (text_space - text_height) // 2 - 5 
        
        draw.text((x, y), text, fill="black", font=font)
        
        # 6. Save the final image
        filepath = os.path.join(OUTPUT_DIR, f"qr_device_{qr_id}.png")
        new_img.save(filepath)
        
        # print(f"Saved: {filepath}")


if __name__ == "__main__":
    # create_qr_codes(100, 1000, 100)
    # create_qr_codes(101, 105)
    # create_qr_codes(111)
    create_qr_codes(801, 1000)