import sqlite3

conn = sqlite3.connect("tracking_history.db", check_same_thread=False)
cursor = conn.cursor()

# Tablo oluştur (eğer yoksa)
cursor.execute("""
CREATE TABLE IF NOT EXISTS tracking_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    tracking_number TEXT,
    courier_slug TEXT
)
""")
conn.commit()

def add_tracking(user_id: int, tracking_number: str, slug: str):
    cursor.execute("INSERT INTO tracking_history (user_id, tracking_number, courier_slug) VALUES (?, ?, ?)",
                   (user_id, tracking_number, slug))
    conn.commit()

def get_history(user_id: int):
    cursor.execute("SELECT tracking_number, courier_slug FROM tracking_history WHERE user_id = ?", (user_id,))
    return cursor.fetchall()
