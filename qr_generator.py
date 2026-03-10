import qrcode
import os
from get_sys_net_info import get_local_ip, get_port_number


# --- CONFIGURATION ---
LAPTOP_IP = get_local_ip() 
PORT = get_port_number()
OUTPUT_DIR = "demo_qrs"

def create_qr_codes(start_id: int, end_id: int, skip_by: int = 1):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Detected Local IP: {LAPTOP_IP}")
    print("Generating QR codes...")

    for qr_id in range(start_id, end_id + 1, skip_by):
        url = f"http://{LAPTOP_IP}:{PORT}/?qr_id={qr_id}"
        
        img = qrcode.make(url)
        filepath = os.path.join(OUTPUT_DIR, f"qr_device_{qr_id}.png")
        img.save(filepath)
        
        print(f"Saved: {filepath} -> {url}")


if __name__ == "__main__":
    create_qr_codes(100, 1000, 100)
    # create_qr_codes(101, 105)