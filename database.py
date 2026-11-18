import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "instance" / "labelgizi.sqlite3"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            product_name TEXT,
            brands TEXT,
            quantity TEXT,
            ingredients_text TEXT,
            energy_kcal_100g REAL,
            sugars_100g REAL,
            fat_100g REAL,
            saturated_fat_100g REAL,
            proteins_100g REAL,
            carbohydrates_100g REAL,
            salt_100g REAL,
            image_url TEXT,
            source_url TEXT,
            fetched_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS education_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            content TEXT,
            scraped_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

def save_product(p):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute("""
        INSERT INTO products (
            barcode, product_name, brands, quantity, ingredients_text,
            energy_kcal_100g, sugars_100g, fat_100g, saturated_fat_100g,
            proteins_100g, carbohydrates_100g, salt_100g, image_url,
            source_url, fetched_at
        ) VALUES (
            :barcode, :product_name, :brands, :quantity, :ingredients_text,
            :energy_kcal_100g, :sugars_100g, :fat_100g, :saturated_fat_100g,
            :proteins_100g, :carbohydrates_100g, :salt_100g, :image_url,
            :source_url, :fetched_at
        )
        ON CONFLICT(barcode) DO UPDATE SET
            product_name=excluded.product_name, brands=excluded.brands,
            quantity=excluded.quantity, ingredients_text=excluded.ingredients_text,
            energy_kcal_100g=excluded.energy_kcal_100g, sugars_100g=excluded.sugars_100g,
            fat_100g=excluded.fat_100g, saturated_fat_100g=excluded.saturated_fat_100g,
            proteins_100g=excluded.proteins_100g,
            carbohydrates_100g=excluded.carbohydrates_100g,
            salt_100g=excluded.salt_100g, image_url=excluded.image_url,
            source_url=excluded.source_url, fetched_at=excluded.fetched_at
        """, {**p, "fetched_at": now})

def save_education_article(url, title, content):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute("""
        INSERT INTO education_articles(url, title, content, scraped_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET title=excluded.title,
        content=excluded.content, scraped_at=excluded.scraped_at
        """, (url, title, content, now))

def search_education(query="", limit=8):
    with connect() as conn:
        if query:
            rows = conn.execute("""
                SELECT title, content, url, scraped_at FROM education_articles
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY scraped_at DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT title, content, url, scraped_at FROM education_articles
                ORDER BY scraped_at DESC LIMIT ?
            """, (limit,)).fetchall()
    return [dict(row) for row in rows]

def save_chat_message(role, message):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute("INSERT INTO chat_messages(role, message, created_at) VALUES (?, ?, ?)",
                     (role, message, now))

def get_recent_messages(limit=30):
    with connect() as conn:
        rows = conn.execute("""
            SELECT role, message, created_at FROM chat_messages
            ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(row) for row in reversed(rows)]
