import aiosqlite
import datetime

DB_NAME = "bot_database.db"

async def init_db(main_admin_id):
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
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                photo_id TEXT,
                price_whole INTEGER,
                price_slice INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id TEXT PRIMARY KEY
            )
        ''')
        await db.execute('INSERT OR IGNORE INTO admins (admin_id) VALUES (?)', (str(main_admin_id),))
        await db.commit()

# ----- USERS -----
async def add_user(user_id, full_name, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, full_name, username) 
            VALUES (?, ?, ?)
        ''', (user_id, full_name, username))
        await db.commit()

# ----- ADMINS -----
async def add_admin(admin_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO admins (admin_id) VALUES (?)', (str(admin_id),))
        await db.commit()

async def get_admins():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT admin_id FROM admins') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def delete_admin(admin_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM admins WHERE admin_id = ?', (str(admin_id),))
        await db.commit()

# ----- PRODUCTS -----
async def add_product(name, photo_id, price_whole, price_slice):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO products (name, photo_id, price_whole, price_slice)
            VALUES (?, ?, ?, ?)
        ''', (name, photo_id, price_whole, price_slice))
        await db.commit()

async def get_products():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM products') as cursor:
            return await cursor.fetchall()

async def get_product(product_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM products WHERE id = ?', (product_id,)) as cursor:
            return await cursor.fetchone()

async def delete_product(product_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM products WHERE id = ?', (product_id,))
        await db.commit()

# ----- ORDERS -----
async def create_order(user_id, order_text, phone, address, price, latitude=None, longitude=None):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            INSERT INTO orders (user_id, order_text, phone, address, latitude, longitude, status, price)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
        ''', (user_id, order_text, phone, address, latitude, longitude, price))
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

# ----- STATISTICS -----
async def get_statistics():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute("SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND date(created_at) = date('now')") as cursor:
            today = await cursor.fetchone()
            
        async with db.execute("SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= date('now', '-7 days')") as cursor:
            weekly = await cursor.fetchone()
            
        async with db.execute("SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= date('now', 'start of month')") as cursor:
            monthly = await cursor.fetchone()
            
        return dict(today), dict(weekly), dict(monthly)

async def reset_statistics():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM orders")
        await db.commit()
