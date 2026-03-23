from nicegui import ui, app, Client
import database
import asyncio
from get_sys_net_info import port_number
from datetime import datetime

# For local testing, we redirect to a mock page within our own app
# AUDIT_SYSTEM_BASE_URL = "/mock_audit/"
# --- CONFIGURATION VARIABLE ---
ENABLE_AUDIT_WARNING = True
LOGIN_REQUIRED = ENABLE_AUDIT_WARNING

@ui.page('/')
async def index(client: Client, qr_id: int = None):
    if LOGIN_REQUIRED:
        # Grab the IP and check if they are logged in
        client_ip = client.ip
        current_user = await database.get_current_user(client_ip)
        if not current_user:
            ui.notify('Authentication required. Redirecting to login...', type='warning')
            ui.navigate.to('/login')
            return
        

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
        if ENABLE_AUDIT_WARNING:
            # Grab the IP and check if they are logged in
            client_ip = client.ip
            current_user = await database.get_current_user(client_ip)


            # Check the new timestamp database
            last_audit = await database.get_last_audit(qr_id)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            clipboard_text = f"Auditor: {current_user}, Time: {current_time}"

            if last_audit:
                # Scenario A: It has been audited before
                with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md border-t-4 border-yellow-500'):
                    ui.icon('warning', size='4rem').classes('text-yellow-500 mb-2')
                    ui.label('Already Audited').classes('text-2xl font-bold mb-2')
                    ui.label(f'This device was last checked on:').classes('text-gray-600')
                    ui.label(f'{last_audit}').classes('text-lg font-bold text-gray-800')
                    ui.label(f'Current User: {current_user}').classes('text-gray-600')
                    ui.label(f'Clipboard Text:').classes('text-gray-600')
                    ui.label(f'{clipboard_text}').classes('text-gray-600')

                    
                    async def proceed_and_copy():
                        # ui.clipboard.write(current_time)
                        ui.clipboard.write(clipboard_text)
                        await database.record_audit(qr_id)
                        ui.notify('Time copied to clipboard! Redirecting...', type='info')
                        # await asyncio.sleep(1)
                        ui.navigate.to(f"http://inbgastmgmt01.qscaudio.com/hardware/{device_id}")

                    ui.button('Continue to Inventory', on_click=proceed_and_copy).classes('w-full bg-red-600 text-white font-bold')
            else:
                # Scenario B: It is mapped, but never audited before
                with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md border-t-4 border-blue-500'):
                    ui.icon('assignment', size='4rem').classes('text-blue-500 mb-2')
                    ui.label('Ready for Audit').classes('text-2xl font-bold mb-2')
                    ui.label('First time auditing this device.').classes('text-gray-600 mb-6')
                    
                    async def initial_audit_and_copy():
                        ui.clipboard.write(clipboard_text)
                        await database.record_audit(qr_id)
                        ui.notify('Time copied to clipboard! Redirecting...', type='info')
                        # await asyncio.sleep(1)
                        ui.navigate.to(f"http://inbgastmgmt01.qscaudio.com/hardware/{device_id}")

                    ui.button('Continue to Inventory', on_click=initial_audit_and_copy).classes('w-full bg-blue-600 text-white font-bold')
        else:
            # Original Behavior: If toggle is False, just bypass everything and redirect instantly
            ui.navigate.to(f"http://inbgastmgmt01.qscaudio.com/hardware/{device_id}")

        # Redirect if mapping exists
        # ui.navigate.to(f"{AUDIT_SYSTEM_BASE_URL}{device_id}")
        # ui.navigate.to("http://inbgastmgmt01.qscaudio.com/account/view-assets")
        print(f"Going to: http://inbgastmgmt01.qscaudio.com/hardware/{device_id}")
        # ui.navigate.to(f"http://inbgastmgmt01.qscaudio.com/hardware/{device_id}")
    else:
        # Show UI if no mapping exists
        with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md'):
            ui.label(f'Unmapped QR Code: #{qr_id}').classes('text-2xl font-bold mb-4')
            ui.label('Enter Device ID to establish a link.').classes('text-gray-600 mb-4')
            
            dev_id_input = ui.input('URL ID (last number in URL)').classes('w-full mb-4')
            
            async def save_mapping():
                val = dev_id_input.value
                if not val:
                    ui.notify('Device ID cannot be empty', type='negative')
                    return
                
                await database.map_qr_to_device(qr_id, val)
                ui.notify(f'Linked QR {qr_id} to {val}. Redirecting...', type='positive')
                await asyncio.sleep(1.5) 
                ui.navigate.to(f"http://inbgastmgmt01.qscaudio.com/hardware/{val}")


            ui.button('Link Device', on_click=save_mapping).classes('w-full bg-blue-600 text-white')
            dev_id_input.on('keydown.enter', save_mapping)


# --- HIDDEN EDIT PAGE ---
@ui.page('/modify')
async def edit_mapping():
    with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md border-t-4 border-orange-500'):
        ui.icon('edit_note', size='4rem').classes('text-orange-500 mb-2')
        ui.label('Modify QR Mapping').classes('text-2xl font-bold mb-1')
        ui.label('Authorized Personnel Only').classes('text-xs text-red-500 font-bold tracking-widest mb-6 uppercase')
        
        qr_input = ui.input('QR Code ID (e.g., 100)').classes('w-full mb-4')
        new_dev_input = ui.input('URL ID').classes('w-full mb-6')

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

@ui.page('/login')
async def login_page(client: Client):
    client_ip = client.ip
    
    with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md border-t-4 border-blue-500'):
        ui.icon('badge', size='4rem').classes('text-blue-500 mb-2')
        ui.label('Auditor Login').classes('text-2xl font-bold mb-4')
        ui.label('Enter your name to begin scanning.').classes('text-gray-600 mb-6 text-center')
        
        name_input = ui.input('Your Name').classes('w-full mb-4')
        
        async def perform_login():
            if not name_input.value:
                ui.notify('Name is required.', type='negative')
                return
            
            await database.login_user(client_ip, name_input.value)
            ui.notify(f'Welcome, {name_input.value}! IP Logged.', type='positive')
            await asyncio.sleep(1)
            ui.navigate.to('/')
            
        name_input.on('keydown.enter', perform_login)
        ui.button('Log In', on_click=perform_login).classes('w-full bg-blue-600 text-white font-bold')

@ui.page('/logout')
async def logout_page(client: Client):
    client_ip = client.ip
    await database.logout_user(client_ip)
    
    with ui.card().classes('w-96 mx-auto mt-20 p-6 items-center shadow-md'):
        ui.icon('logout', size='4rem').classes('text-gray-500 mb-2')
        ui.label('Logged Out').classes('text-2xl font-bold mb-4')
        ui.label('Your device IP has been cleared.').classes('text-gray-600 mb-6')
        ui.button('Log Back In', on_click=lambda: ui.navigate.to('/login')).classes('w-full bg-gray-600 text-white')



# # --- MOCK COMPANY LAN PAGE FOR TESTING ---
# @ui.page('/mock_audit/{device_id}')
# def mock_audit_page(device_id: str):
#     with ui.column().classes('w-full items-center mt-20'):
#         ui.icon('check_circle', size='4rem').classes('text-green-500 mb-4')
#         ui.label('SUCCESS: Redirected to Auditing System').classes('text-2xl font-bold')
#         ui.label(f'You are now viewing the audit page for: {device_id}').classes('text-xl mt-4')

app.on_startup(database.init_db)
ui.run(title='Device Auditing Mapper', port=port_number, host='0.0.0.0')