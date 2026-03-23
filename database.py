import aiosqlite

DB_FILE = 'qsys_auditing_poc.db'

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('PRAGMA journal_mode=WAL;') 
        await db.execute('''
            CREATE TABLE IF NOT EXISTS qr_mapping (
                qr_id INTEGER PRIMARY KEY,
                device_id TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                qr_id INTEGER PRIMARY KEY, 
                last_audited DATETIME
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                ip_address TEXT PRIMARY KEY,
                username TEXT
            )
        ''')
        await db.commit()


async def get_device_id(qr_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute('SELECT device_id FROM qr_mapping WHERE qr_id = ?', (qr_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def map_qr_to_device(qr_id: int, device_id: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('INSERT OR REPLACE INTO qr_mapping (qr_id, device_id) VALUES (?, ?)', (qr_id, device_id))
        await db.commit()

async def get_last_audit(qr_id: int):
    async with aiosqlite.connect('qsys_auditing_poc.db') as db:
        async with db.execute('SELECT last_audited FROM audit_logs WHERE qr_id = ?', (qr_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def record_audit(qr_id: int):
    async with aiosqlite.connect('qsys_auditing_poc.db') as db:
        # INSERT OR REPLACE acts as an update if the qr_id already exists
        await db.execute('''
            INSERT OR REPLACE INTO audit_logs (qr_id, last_audited) 
            VALUES (?, datetime('now', 'localtime'))
        ''', (qr_id,))
        await db.commit()

async def login_user(ip: str, username: str):
    async with aiosqlite.connect('qsys_auditing_poc.db') as db:
        # INSERT OR REPLACE handles if they log in again with a different name
        await db.execute('INSERT OR REPLACE INTO active_sessions (ip_address, username) VALUES (?, ?)', (ip, username))
        await db.commit()

async def logout_user(ip: str):
    async with aiosqlite.connect('qsys_auditing_poc.db') as db:
        await db.execute('DELETE FROM active_sessions WHERE ip_address = ?', (ip,))
        await db.commit()

async def get_current_user(ip: str):
    async with aiosqlite.connect('qsys_auditing_poc.db') as db:
        async with db.execute('SELECT username FROM active_sessions WHERE ip_address = ?', (ip,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None