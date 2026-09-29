import sqlite3
from datetime import datetime, timedelta


DATABASE = "database.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            brand TEXT,
            model TEXT,
            year INTEGER,
            mileage INTEGER,
            gearbox TEXT,
            engine TEXT,
            price TEXT,
            city TEXT,
            description TEXT,
            contact TEXT,
            photo_id TEXT,
            status TEXT DEFAULT 'draft',
            paid INTEGER DEFAULT 0,
            payment_id TEXT,
            published_at TEXT,
            expires_at TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def create_ad(user_id):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO ads (user_id, status, paid)
        VALUES (?, 'draft', 0)
        """,
        (user_id,)
    )

    ad_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return ad_id


def update_ad(ad_id, field, value):
    allowed_fields = {
        "brand",
        "model",
        "year",
        "mileage",
        "gearbox",
        "engine",
        "price",
        "city",
        "description",
        "contact",
        "photo_id",
        "status",
        "paid",
        "payment_id",
        "published_at",
        "expires_at",
    }

    if field not in allowed_fields:
        raise ValueError("Недопустимое поле.")

    connection = get_connection()

    connection.execute(
        f"UPDATE ads SET {field} = ? WHERE id = ?",
        (value, ad_id)
    )

    connection.commit()
    connection.close()


def mark_paid(ad_id, payment_id):
    connection = get_connection()

    connection.execute(
        """
        UPDATE ads
        SET paid = 1,
            payment_id = ?,
            status = 'moderation'
        WHERE id = ?
        """,
        (payment_id, ad_id)
    )

    connection.commit()
    connection.close()


def publish_ad(ad_id):
    published_at = datetime.now()
    expires_at = published_at + timedelta(days=10)

    connection = get_connection()

    connection.execute(
        """
        UPDATE ads
        SET status = 'published',
            published_at = ?,
            expires_at = ?
        WHERE id = ?
        """,
        (
            published_at.isoformat(),
            expires_at.isoformat(),
            ad_id,
        )
    )

    connection.commit()
    connection.close()


def get_ad(ad_id):
    connection = get_connection()

    ad = connection.execute(
        "SELECT * FROM ads WHERE id = ?",
        (ad_id,)
    ).fetchone()

    connection.close()

    return ad