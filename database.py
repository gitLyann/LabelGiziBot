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
    seed_education_articles()


def seed_education_articles():
    """Isi materi ringkas lokal agar chatbot tetap berguna saat scraping gagal.

    Materi ini adalah ringkasan edukatif untuk demo, bukan hasil scraping otomatis.
    URL sumber resmi disimpan agar pengguna dapat membaca informasi lengkap.
    """
    articles = [
        (
            "local://label-gizi",
            "Cara membaca label informasi nilai gizi",
            "Untuk membaca label gizi pada kemasan, perhatikan takaran saji dan jumlah sajian per kemasan terlebih dahulu. "
            "Angka energi dan zat gizi pada tabel biasanya dinyatakan per takaran saji atau per 100 gram/ml sesuai format label. "
            "Periksa energi total, lemak, lemak jenuh, protein, karbohidrat, gula, dan natrium. "
            "Persen AKG membantu memperkirakan kontribusi zat gizi terhadap kebutuhan harian acuan; kebutuhan setiap orang dapat berbeda. "
            "Jika membandingkan dua produk, gunakan dasar takaran yang sama. Jangan menyimpulkan produk sehat hanya dari satu angka. "
            "Periksa juga daftar bahan dan informasi alergen pada kemasan. Selalu utamakan label fisik terbaru karena data daring dapat tidak lengkap. "
            "Sumber bacaan: Kementerian Kesehatan RI, Ayo Sehat: https://ayosehat.kemkes.go.id/"
        ),
        (
            "local://isi-piringku",
            "Panduan Isi Piringku dan gizi seimbang",
            "Isi Piringku adalah panduan visual untuk membantu membiasakan pola makan beragam dan seimbang. "
            "Secara umum, dalam satu piring makan, sekitar setengah bagian diisi sayur dan buah, sedangkan setengah lainnya diisi makanan pokok dan lauk-pauk. "
            "Utamakan variasi bahan pangan, cukup minum air, membiasakan aktivitas fisik, serta menjaga kebersihan. "
            "Kebutuhan porsi dapat berbeda menurut usia, aktivitas, kondisi kesehatan, dan kebutuhan individu. "
            "Panduan ini bersifat edukasi umum, bukan pengganti saran tenaga kesehatan. "
            "Sumber bacaan: Kementerian Kesehatan RI, Ayo Sehat: https://ayosehat.kemkes.go.id/isi-piringku-kebutuhan-gizi-harian-seimbang"
        ),
        (
            "local://gula-garam-lemak",
            "Mengenali gula, garam, dan lemak pada makanan kemasan",
            "Saat memilih makanan kemasan, periksa kandungan gula, natrium (yang berkaitan dengan garam), lemak total, dan lemak jenuh pada label. "
            "Perhatikan ukuran takaran saji: jumlah yang dikonsumsi bisa lebih dari satu sajian sehingga asupan aktual dapat lebih besar daripada angka untuk satu sajian. "
            "Bandingkan produk sejenis dengan ukuran sajian yang setara dan jangan menganggap data yang kosong sebagai nol. "
            "Ikuti anjuran kesehatan resmi dan konsultasikan kebutuhan khusus kepada tenaga kesehatan. "
            "Sumber bacaan: Kementerian Kesehatan RI, Ayo Sehat: https://ayosehat.kemkes.go.id/"
        ),
    ]
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO education_articles(url, title, content, scraped_at)
            VALUES (?, ?, ?, ?)
        """, [(url, title, content, now) for url, title, content in articles])

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
    """Cari artikel berdasarkan kata kunci, bukan seluruh kalimat pengguna."""
    import re
    words = [w for w in re.findall(r"[a-zA-Z0-9]+", (query or "").lower())
             if len(w) >= 3 and w not in {"bagaimana", "apakah", "dengan", "untuk", "yang", "dari", "cara", "bisa", "saya", "pada"}]
    with connect() as conn:
        if words:
            clauses = " OR ".join(["LOWER(title) LIKE ? OR LOWER(content) LIKE ?" for _ in words])
            params = []
            for word in words:
                params.extend([f"%{word}%", f"%{word}%"])
            rows = conn.execute(f"""
                SELECT title, content, url, scraped_at FROM education_articles
                WHERE {clauses}
                ORDER BY scraped_at DESC LIMIT ?
            """, (*params, limit)).fetchall()
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
