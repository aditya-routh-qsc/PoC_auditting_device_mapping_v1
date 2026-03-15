# Device Auditing QR Mapping System (PoC)

A complete, asynchronous Proof of Concept (PoC) designed to bridge physical hardware auditing with digital databases on a local network. 

This system provides a dynamic web interface for scanning and mapping QR codes to specific Device IDs, alongside a fully automated Python pipeline for generating, formatting, and packaging print-ready physical QR asset grids.

## 🚀 Features

* **Dynamic Redirection:** Scanned QR codes automatically redirect the user to the target device's specific audit page via GET protocol parameters.
* **On-the-Fly Mapping:** Unmapped QR codes present a mobile-friendly UI to instantly link the physical code to a Device ID in the database.
* **Concurrency-Safe Database:** Utilizes `aiosqlite` with Write-Ahead Logging (WAL) to ensure non-blocking, simultaneous database reads/writes by multiple auditors.
* **Automated Asset Generation:** A 3-step automated pipeline that generates individual QR codes, packs them into centered A4 grids with cutting guides, compiles them into a single PDF, and automatically cleans up intermediate image files to prevent disk bloat.
* **Network Auto-Discovery:** Automatically detects the host machine's local LAN IP address via a dummy socket connection for seamless local network deployment.

## 🛠️ Prerequisites & Installation

Ensure you have Python 3.8+ installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 📁 Project Structure

* `main.py` - The core NiceGUI web server, UI components, and routing logic.
* `database.py` - Asynchronous SQLite database management and query functions.
* `get_sys_net_info.py` - Utility to fetch the dynamic local LAN IP.
* `qr_generator.py` - Generates individual QR codes with ID text centered below.
* `generate_printable_grid.py` - Packs single QRs into perfectly centered A4 grids with dotted cutting lines.
* `generate_pdf.py` - Bundles A4 grids into a final, print-ready PDF and cleans up the working directory.

## 🖥️ Operating the Web Application

To start the auditing server, simply run the main file:

```bash
python main.py
```

The server will automatically bind to your local IP. 
* **Auditor Portal (Homepage):** Access `http://<YOUR_LAN_IP>:<PORT>/` to manually enter a QR ID or handle automatic scan redirects.
* **Admin Dashboard:** Access `http://<YOUR_LAN_IP>:<PORT>/modify` to update or correct existing QR-to-Device mappings.

## 🖨️ Operating the Automated QR Print Pipeline

When you need to generate a new batch of physical QR stickers for hardware deployment, run the pipeline in this exact sequence:

1. **Generate the Raw Codes:**
```bash
python qr_generator.py
```
*This populates the `demo_qrs/` folder with individual PNGs.*

2. **Pack into Printable A4 Grids:**
```bash
python generate_printable_grid.py
```
*This packs the codes into centered grids with cutting guides, saves them to `printable_sheets/`, and automatically deletes the raw PNGs from step 1.*

3. **Compile into PDF:**
```bash
python generate_pdf.py
```
*This bundles the A4 sheets into a single `qrcodes-pdf.pdf` file, gracefully overwrites any older versions (if not currently open), and automatically cleans up the intermediate A4 sheets.*

## 🔒 Future Production Scope

* **Static Hosting:** Migrate from dynamic IP detection to an IT-assigned static IP or internal DNS hostname (e.g., `audit.company.local`) to ensure printed QR links remain permanent.
* **Access Control:** Implement role-based authentication to secure the `/modify` routing endpoint.
* **Audit Trail:** Expand the database schema to log timestamps and historical mapping changes.
