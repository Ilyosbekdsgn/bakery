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
                price_slice INTEGER,
                discount_whole INTEGER DEFAULT 0,
                discount_slice INTEGER DEFAULT 0
            )
        ''')
        # Alter table for existing data
        try:
            await db.execute('ALTER TABLE products ADD COLUMN discount_whole INTEGER DEFAULT 0')
            await db.execute('ALTER TABLE products ADD COLUMN discount_slice INTEGER DEFAULT 0')
        except:
            pass

        await db.execute('''
            CREATE TABLE IF NOT EXISTS cakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                photo_id TEXT,
                price INTEGER,
                description TEXT,
                discount_amount INTEGER DEFAULT 0
            )
        ''')
        try:
            await db.execute('ALTER TABLE cakes ADD COLUMN discount_amount INTEGER DEFAULT 0')
        except:
            pass

        await db.execute('''
            CREATE TABLE IF NOT EXISTS fast_foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                photo_id TEXT,
                price INTEGER,
                description TEXT,
                discount_amount INTEGER DEFAULT 0
            )
        ''')
        try:
            await db.execute('ALTER TABLE fast_foods ADD COLUMN discount_amount INTEGER DEFAULT 0')
        except:
            pass
            
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS custom_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT,
                photo_id TEXT,
                price INTEGER,
                description TEXT,
                discount_amount INTEGER DEFAULT 0,
                FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        ''')
        try:
            await db.execute('ALTER TABLE custom_products ADD COLUMN discount_amount INTEGER DEFAULT 0')
        except:
            pass

        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id TEXT PRIMARY KEY
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price INTEGER
            )
        ''')
        await db.execute('INSERT OR IGNORE INTO admins (admin_id) VALUES (?)', (str(main_admin_id),))
        await db.commit()

# ----- SETTINGS -----
async def is_discount_active():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT value FROM settings WHERE key = 'thursday_discount'") as cursor:
            row = await cursor.fetchone()
            return True if row and row[0] == '1' else False

async def set_discount_status(active: bool):
    async with aiosqlite.connect(DB_NAME) as db:
        val = '1' if active else '0'
        await db.execute("INSERT INTO settings (key, value) VALUES ('thursday_discount', ?) ON CONFLICT(key) DO UPDATE SET value = ?", (val, val))
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

async def update_product_discount(product_id, discount_whole, discount_slice):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET discount_whole = ?, discount_slice = ? WHERE id = ?', (discount_whole, discount_slice, product_id))
        await db.commit()

async def delete_product(product_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM products WHERE id = ?', (product_id,))
        await db.commit()

# ----- FAST FOODS -----
async def add_fast_food(name, photo_id, price, description):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO fast_foods (name, photo_id, price, description)
            VALUES (?, ?, ?, ?)
        ''', (name, photo_id, price, description))
        await db.commit()

async def get_fast_foods():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM fast_foods') as cursor:
            return await cursor.fetchall()

async def get_fast_food(fast_food_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM fast_foods WHERE id = ?', (fast_food_id,)) as cursor:
            return await cursor.fetchone()

async def update_fast_food_discount(fast_food_id, discount_amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE fast_foods SET discount_amount = ? WHERE id = ?', (discount_amount, fast_food_id))
        await db.commit()

async def delete_fast_food(fast_food_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM fast_foods WHERE id = ?', (fast_food_id,))
        await db.commit()


# ----- CAKES -----
async def add_cake(name, photo_id, price, description):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO cakes (name, photo_id, price, description)
            VALUES (?, ?, ?, ?)
        ''', (name, photo_id, price, description))
        await db.commit()

async def get_cakes():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM cakes') as cursor:
            return await cursor.fetchall()

async def get_cake(cake_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM cakes WHERE id = ?', (cake_id,)) as cursor:
            return await cursor.fetchone()

async def update_cake_discount(cake_id, discount_amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE cakes SET discount_amount = ? WHERE id = ?', (discount_amount, cake_id))
        await db.commit()

async def delete_cake(cake_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM cakes WHERE id = ?', (cake_id,))
        await db.commit()

# ----- CATEGORIES & CUSTOM PRODUCTS -----
async def add_category(name):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (name,))
        await db.commit()
        return cursor.lastrowid

async def get_categories():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM categories') as cursor:
            return await cursor.fetchall()

async def get_category(category_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM categories WHERE id = ?', (category_id,)) as cursor:
            return await cursor.fetchone()

async def delete_category(category_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        await db.execute('DELETE FROM custom_products WHERE category_id = ?', (category_id,))
        await db.commit()

async def add_custom_product(category_id, name, photo_id, price, description):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO custom_products (category_id, name, photo_id, price, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (category_id, name, photo_id, price, description))
        await db.commit()

async def get_custom_products(category_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM custom_products WHERE category_id = ?', (category_id,)) as cursor:
            return await cursor.fetchall()

async def get_all_custom_products():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM custom_products') as cursor:
            return await cursor.fetchall()

async def get_custom_product(product_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM custom_products WHERE id = ?', (product_id,)) as cursor:
            return await cursor.fetchone()

async def update_custom_product_discount(product_id, discount_amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE custom_products SET discount_amount = ? WHERE id = ?', (discount_amount, product_id))
        await db.commit()

async def delete_custom_product(product_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM custom_products WHERE id = ?', (product_id,))
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

# ----- CARTS -----
async def add_to_cart(user_id, product_name, quantity, price):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO carts (user_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (user_id, product_name, quantity, price))
        await db.commit()

async def get_cart(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM carts WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchall()

async def clear_cart(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM carts WHERE user_id = ?', (user_id,))
        await db.commit()

async def remove_from_cart(cart_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM carts WHERE cart_id = ?', (cart_id,))
        await db.commit()
