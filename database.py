import asyncpg
import os
import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

async def init_db(main_admin_id):
    db = await get_db()
    try:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                phone TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id BIGINT,
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
                id SERIAL PRIMARY KEY,
                name TEXT,
                photo_id TEXT,
                price_whole INTEGER,
                price_slice INTEGER,
                discount_whole INTEGER DEFAULT 0,
                discount_slice INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS cakes (
                id SERIAL PRIMARY KEY,
                name TEXT,
                photo_id TEXT,
                price INTEGER,
                description TEXT,
                discount_amount INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS fast_foods (
                id SERIAL PRIMARY KEY,
                name TEXT,
                photo_id TEXT,
                price INTEGER,
                description TEXT,
                discount_amount INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS custom_products (
                id SERIAL PRIMARY KEY,
                category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                name TEXT,
                photo_id TEXT,
                price INTEGER,
                description TEXT,
                discount_amount INTEGER DEFAULT 0
            )
        ''')
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
                cart_id SERIAL PRIMARY KEY,
                user_id BIGINT,
                product_name TEXT,
                quantity INTEGER,
                price INTEGER,
                photo_id TEXT
            )
        ''')
        await db.execute(
            'INSERT INTO admins (admin_id) VALUES ($1) ON CONFLICT DO NOTHING',
            str(main_admin_id)
        )
    finally:
        await db.close()

# ----- SETTINGS -----
async def is_discount_active():
    db = await get_db()
    try:
        row = await db.fetchrow("SELECT value FROM settings WHERE key = 'thursday_discount'")
        return True if row and row['value'] == '1' else False
    finally:
        await db.close()

async def set_discount_status(active: bool):
    db = await get_db()
    try:
        val = '1' if active else '0'
        await db.execute(
            "INSERT INTO settings (key, value) VALUES ('thursday_discount', $1) ON CONFLICT (key) DO UPDATE SET value = $1",
            val
        )
    finally:
        await db.close()

# ----- USERS -----
async def add_user(user_id, full_name, username):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO users (user_id, full_name, username) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING',
            user_id, full_name, username
        )
    finally:
        await db.close()

# ----- ADMINS -----
async def add_admin(admin_id):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO admins (admin_id) VALUES ($1) ON CONFLICT DO NOTHING',
            str(admin_id)
        )
    finally:
        await db.close()

async def get_admins():
    db = await get_db()
    try:
        rows = await db.fetch('SELECT admin_id FROM admins')
        return [row['admin_id'] for row in rows]
    finally:
        await db.close()

async def delete_admin(admin_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM admins WHERE admin_id = $1', str(admin_id))
    finally:
        await db.close()

# ----- PRODUCTS -----
async def add_product(name, photo_id, price_whole, price_slice):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO products (name, photo_id, price_whole, price_slice) VALUES ($1, $2, $3, $4)',
            name, photo_id, price_whole, price_slice
        )
    finally:
        await db.close()

async def get_products():
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM products')
    finally:
        await db.close()

async def get_product(product_id):
    db = await get_db()
    try:
        return await db.fetchrow('SELECT * FROM products WHERE id = $1', product_id)
    finally:
        await db.close()

async def update_product_discount(product_id, discount_whole, discount_slice):
    db = await get_db()
    try:
        await db.execute(
            'UPDATE products SET discount_whole = $1, discount_slice = $2 WHERE id = $3',
            discount_whole, discount_slice, product_id
        )
    finally:
        await db.close()

async def delete_product(product_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM products WHERE id = $1', product_id)
    finally:
        await db.close()

# ----- FAST FOODS -----
async def add_fast_food(name, photo_id, price, description):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO fast_foods (name, photo_id, price, description) VALUES ($1, $2, $3, $4)',
            name, photo_id, price, description
        )
    finally:
        await db.close()

async def get_fast_foods():
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM fast_foods')
    finally:
        await db.close()

async def get_fast_food(fast_food_id):
    db = await get_db()
    try:
        return await db.fetchrow('SELECT * FROM fast_foods WHERE id = $1', fast_food_id)
    finally:
        await db.close()

async def update_fast_food_discount(fast_food_id, discount_amount):
    db = await get_db()
    try:
        await db.execute(
            'UPDATE fast_foods SET discount_amount = $1 WHERE id = $2',
            discount_amount, fast_food_id
        )
    finally:
        await db.close()

async def delete_fast_food(fast_food_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM fast_foods WHERE id = $1', fast_food_id)
    finally:
        await db.close()

# ----- CAKES -----
async def add_cake(name, photo_id, price, description):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO cakes (name, photo_id, price, description) VALUES ($1, $2, $3, $4)',
            name, photo_id, price, description
        )
    finally:
        await db.close()

async def get_cakes():
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM cakes')
    finally:
        await db.close()

async def get_cake(cake_id):
    db = await get_db()
    try:
        return await db.fetchrow('SELECT * FROM cakes WHERE id = $1', cake_id)
    finally:
        await db.close()

async def update_cake_discount(cake_id, discount_amount):
    db = await get_db()
    try:
        await db.execute(
            'UPDATE cakes SET discount_amount = $1 WHERE id = $2',
            discount_amount, cake_id
        )
    finally:
        await db.close()

async def delete_cake(cake_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM cakes WHERE id = $1', cake_id)
    finally:
        await db.close()

# ----- CATEGORIES & CUSTOM PRODUCTS -----
async def add_category(name):
    db = await get_db()
    try:
        row = await db.fetchrow(
            'INSERT INTO categories (name) VALUES ($1) ON CONFLICT DO NOTHING RETURNING id',
            name
        )
        return row['id'] if row else None
    finally:
        await db.close()

async def get_categories():
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM categories')
    finally:
        await db.close()

async def get_category(category_id):
    db = await get_db()
    try:
        return await db.fetchrow('SELECT * FROM categories WHERE id = $1', category_id)
    finally:
        await db.close()

async def delete_category(category_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM custom_products WHERE category_id = $1', category_id)
        await db.execute('DELETE FROM categories WHERE id = $1', category_id)
    finally:
        await db.close()

async def add_custom_product(category_id, name, photo_id, price, description):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO custom_products (category_id, name, photo_id, price, description) VALUES ($1, $2, $3, $4, $5)',
            category_id, name, photo_id, price, description
        )
    finally:
        await db.close()

async def get_custom_products(category_id):
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM custom_products WHERE category_id = $1', category_id)
    finally:
        await db.close()

async def get_all_custom_products():
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM custom_products')
    finally:
        await db.close()

async def get_custom_product(product_id):
    db = await get_db()
    try:
        return await db.fetchrow('SELECT * FROM custom_products WHERE id = $1', product_id)
    finally:
        await db.close()

async def update_custom_product_discount(product_id, discount_amount):
    db = await get_db()
    try:
        await db.execute(
            'UPDATE custom_products SET discount_amount = $1 WHERE id = $2',
            discount_amount, product_id
        )
    finally:
        await db.close()

async def delete_custom_product(product_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM custom_products WHERE id = $1', product_id)
    finally:
        await db.close()

# ----- ORDERS -----
async def create_order(user_id, order_text, phone, address, price, latitude=None, longitude=None):
    db = await get_db()
    try:
        row = await db.fetchrow('''
            INSERT INTO orders (user_id, order_text, phone, address, latitude, longitude, status, price)
            VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7)
            RETURNING order_id
        ''', user_id, order_text, phone, address, latitude, longitude, price)
        return row['order_id']
    finally:
        await db.close()

async def update_order_status(order_id, status):
    db = await get_db()
    try:
        await db.execute('UPDATE orders SET status = $1 WHERE order_id = $2', status, order_id)
    finally:
        await db.close()

async def update_order_price(order_id, price):
    db = await get_db()
    try:
        await db.execute('UPDATE orders SET price = $1 WHERE order_id = $2', price, order_id)
    finally:
        await db.close()

async def get_order(order_id):
    db = await get_db()
    try:
        return await db.fetchrow('SELECT * FROM orders WHERE order_id = $1', order_id)
    finally:
        await db.close()

# ----- STATISTICS -----
async def get_statistics():
    db = await get_db()
    try:
        today = await db.fetchrow(
            "SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND DATE(created_at) = CURRENT_DATE"
        )
        weekly = await db.fetchrow(
            "SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= CURRENT_DATE - INTERVAL '7 days'"
        )
        monthly = await db.fetchrow(
            "SELECT COUNT(DISTINCT user_id) as clients, SUM(price) as revenue FROM orders WHERE status != 'cancelled' AND created_at >= DATE_TRUNC('month', CURRENT_DATE)"
        )
        return dict(today), dict(weekly), dict(monthly)
    finally:
        await db.close()

async def reset_statistics():
    db = await get_db()
    try:
        await db.execute("DELETE FROM orders")
    finally:
        await db.close()

# ----- CARTS -----
async def add_to_cart(user_id, product_name, quantity, price, photo_id=None):
    db = await get_db()
    try:
        await db.execute(
            'INSERT INTO carts (user_id, product_name, quantity, price, photo_id) VALUES ($1, $2, $3, $4, $5)',
            user_id, product_name, quantity, price, photo_id
        )
    finally:
        await db.close()

async def get_cart(user_id):
    db = await get_db()
    try:
        return await db.fetch('SELECT * FROM carts WHERE user_id = $1', user_id)
    finally:
        await db.close()

async def clear_cart(user_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM carts WHERE user_id = $1', user_id)
    finally:
        await db.close()

async def remove_from_cart(cart_id):
    db = await get_db()
    try:
        await db.execute('DELETE FROM carts WHERE cart_id = $1', cart_id)
    finally:
        await db.close()
