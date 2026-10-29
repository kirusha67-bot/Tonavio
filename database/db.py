import sqlite3


DB_PATH = "tonavio.db"


def init_database():
    with sqlite3.connect(DB_PATH) as db:

        # Пользователи Tonavio
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL DEFAULT 'en'
            )
        """)

        # Коллекции Telegram Gifts
        db.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                total_supply INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Конкретные подарки
        db.execute("""
            CREATE TABLE IF NOT EXISTS gifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_gift_id TEXT UNIQUE,
                collection_slug TEXT NOT NULL,
                gift_number INTEGER,
                model TEXT,
                backdrop TEXT,
                pattern TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Листинги с разных маркетплейсов
        db.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gift_id INTEGER,
                marketplace TEXT NOT NULL,
                external_id TEXT,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                listing_url TEXT,
                active INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (gift_id)
                    REFERENCES gifts(id)
            )
        """)

        # История цен
        db.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_slug TEXT NOT NULL,
                model TEXT,
                backdrop TEXT,
                pattern TEXT,
                marketplace TEXT NOT NULL,
                floor_price REAL,
                listings_count INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Подтверждённые продажи
        db.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gift_id INTEGER,
                marketplace TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                sold_at TIMESTAMP,
                external_id TEXT UNIQUE,

                FOREIGN KEY (gift_id)
                    REFERENCES gifts(id)
            )
        """)

        # Сохранённые алерты пользователей
        db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                collection_slug TEXT,
                model TEXT,
                backdrop TEXT,
                pattern TEXT,
                max_price REAL,
                marketplace TEXT,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.commit()


def get_language(user_id: int) -> str:
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute(
            "SELECT language FROM users WHERE telegram_id = ?",
            (user_id,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

        db.execute(
            "INSERT INTO users (telegram_id, language) VALUES (?, ?)",
            (user_id, "en")
        )
        db.commit()

        return "en"


def set_language(user_id: int, language: str):
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            INSERT INTO users (telegram_id, language)
            VALUES (?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET language = excluded.language
        """, (user_id, language))

        db.commit()