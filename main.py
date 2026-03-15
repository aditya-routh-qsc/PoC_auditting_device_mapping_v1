from nicegui import ui, app
import database
import asyncio
from get_sys_net_info import port_number

# For local testing, we redirect to a mock page within our own app
AUDIT_SYSTEM_BASE_URL = "/mock_audit/"

@ui.page('/')
async def index(qr_id: int = None):
    if qr_id is None:
        with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md border-t-4 border-blue-500'):
            ui.icon('qr_code', size='4rem').classes('text-blue-500 mb-2')
            ui.label('Device Audit Portal').classes('text-2xl font-bold mb-2')
            ui.label('Scan a QR code, or manually enter the ID printed on the device.').classes('text-center text-gray-600 mb-6')
            
            def process_manual_entry(): 
                val = manual_qr_input.value
                if not val or not val.isdigit():
                    ui.notify('Please enter a valid numeric QR ID.', type='negative')
                    return
                # Instantly reload this exact same page, but append the GET parameter
                ui.navigate.to(f"/?qr_id={val}")

            manual_qr_input = ui.input('Enter QR ID (e.g., 100)').classes('w-full mb-4').on('keydown.enter', process_manual_entry)

            ui.button('Find Device', on_click=process_manual_entry).classes('w-full bg-blue-600 text-white font-bold')
        return

    # Check database
    device_id = await database.get_device_id(qr_id)

    if device_id:
        # Redirect if mapping exists
        ui.navigate.to(f"{AUDIT_SYSTEM_BASE_URL}{device_id}")
    else:
        # Show UI if no mapping exists
        with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md'):
            ui.label(f'Unmapped QR Code: #{qr_id}').classes('text-2xl font-bold mb-4')
            ui.label('Enter Device ID to establish a link.').classes('text-gray-600 mb-4')
            
            dev_id_input = ui.input('Device ID (e.g., DEV-001)').classes('w-full mb-4')
            
            async def save_mapping():
                val = dev_id_input.value
                if not val:
                    ui.notify('Device ID cannot be empty', type='negative')
                    return
                
                await database.map_qr_to_device(qr_id, val)
                ui.notify(f'Linked QR {qr_id} to {val}. Redirecting...', type='positive')
                await asyncio.sleep(1.5) 
                ui.navigate.to(f"{AUDIT_SYSTEM_BASE_URL}{val}")

            ui.button('Link Device', on_click=save_mapping).classes('w-full bg-blue-600 text-white')



# --- HIDDEN EDIT PAGE ---
@ui.page('/modify')
async def edit_mapping():
    with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md border-t-4 border-orange-500'):
        ui.icon('edit_note', size='4rem').classes('text-orange-500 mb-2')
        ui.label('Modify QR Mapping').classes('text-2xl font-bold mb-1')
        ui.label('Authorized Personnel Only').classes('text-xs text-red-500 font-bold tracking-widest mb-6 uppercase')
        
        qr_input = ui.input('QR Code ID (e.g., 100)').classes('w-full mb-4')
        new_dev_input = ui.input('New Device ID (e.g., QSC-TEST-02)').classes('w-full mb-6')

        async def update_mapping():
            # 1. Basic Validation
            if not qr_input.value or not new_dev_input.value:
                ui.notify('Both fields are required to update a mapping.', type='negative')
                return
            
            try:
                qr_id_int = int(qr_input.value)
            except ValueError:
                ui.notify('QR Code ID must be a valid number.', type='negative')
                return

            # 2. Check current status to provide better feedback
            old_device = await database.get_device_id(qr_id_int)
            
            # 3. Perform the update
            await database.map_qr_to_device(qr_id_int, new_dev_input.value)
            
            if old_device:
                ui.notify(f'Updated! QR #{qr_id_int} moved from {old_device} to {new_dev_input.value}', type='positive')
            else:
                ui.notify(f'Created! QR #{qr_id_int} is now mapped to {new_dev_input.value}', type='positive')
            
            # 4. Clear the form for the next edit
            qr_input.value = ''
            new_dev_input.value = ''

        ui.button('Update Mapping', on_click=update_mapping).classes('w-full bg-orange-600 text-white font-bold')

        qr_input.on('keydown.enter', lambda: new_dev_input.run_method('focus'))
        new_dev_input.on('keydown.enter', update_mapping)


# --- MOCK COMPANY LAN PAGE FOR TESTING ---
@ui.page('/mock_audit/{device_id}')
def mock_audit_page(device_id: str):
    with ui.column().classes('w-full items-center mt-20'):
        ui.icon('check_circle', size='4rem').classes('text-green-500 mb-4')
        ui.label('SUCCESS: Redirected to Auditing System').classes('text-2xl font-bold')
        ui.label(f'You are now viewing the audit page for: {device_id}').classes('text-xl mt-4')

app.on_startup(database.init_db)
ui.run(title='Device Auditing Mapper', port=port_number, host='0.0.0.0')