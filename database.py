import aiosqlite
import datetime

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                phone TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_text TEXT,
                phone TEXT,
                address TEXT,
                latitude REAL,
                longitude REAL,
                status TEXT, 
                price INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def add_user(user_id, full_name, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, full_name, username) 
            VALUES (?, ?, ?)
        ''', (user_id, full_name, username))
        await db.commit()

async def create_order(user_id, order_text, phone, address, latitude=None, longitude=None):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            INSERT INTO orders (user_id, order_text, phone, address, latitude, longitude, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        ''', (user_id, order_text, phone, address, latitude, longitude))
        await db.commit()
        return cursor.lastrowid

async def update_order_status(order_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
        await db.commit()

async def update_order_price(order_id, price):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE orders SET price = ? WHERE order_id = ?', (price, order_id))
        await db.commit()

async def get_order(order_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)) as cursor:
            return await cursor.fetchone()

async def get_statistics():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        
        # Today
        async with db.execute("SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND date(created_at) = date('now')") as cursor:
            today = await cursor.fetchone()
            
        # This Week
        async with db.execute("SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= date('now', '-7 days')") as cursor:
            weekly = await cursor.fetchone()
            
        # This Month
        async with db.execute("SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= date('now', 'start of month')") as cursor:
            monthly = await cursor.fetchone()
            
        return dict(today), dict(weekly), dict(monthly)
