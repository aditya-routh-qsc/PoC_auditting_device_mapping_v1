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