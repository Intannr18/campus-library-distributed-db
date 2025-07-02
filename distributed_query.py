import psycopg2
import redis
from pymongo import MongoClient

# --- PostgreSQL connection ---
pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="admin",
    password="admin",
    dbname="library"
)
pg_cursor = pg_conn.cursor()
pg_cursor.execute("SELECT id, title FROM books")
books = pg_cursor.fetchall()

# --- MongoDB connection ---
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["library"]
reviews_col = mongo_db["reviews"]

# --- Redis connection ---
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# --- Combine data from all sources ---
print("📚 Daftar Buku Lengkap dengan Rating & Ketersediaan:")
for book in books:
    book_id, title = book

    # Ambil rating dari MongoDB
    reviews = reviews_col.find({"book_id": book_id})
    ratings = [review["rating"] for review in reviews]
    avg_rating = round(sum(ratings)/len(ratings), 2) if ratings else "N/A"

    # Ambil status dari Redis
    status = redis_client.get(f"book_availability:{book_id}") or "unknown"

    print(f"- {title} | Rating: {avg_rating} | Status: {status}")

# --- Tutup koneksi ---
pg_cursor.close()
pg_conn.close()
mongo_client.close()
