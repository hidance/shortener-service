import os
import secrets
import redis
import psycopg2
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

app = Flask(__name__)


load_dotenv()  # Loads variables from .env file
# --- Bad Practice: Hardcoded credentials (Your task to fix!) --- [fixed]
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST") # In Docker, this will be the service name
DB_PORT = int(os.getenv("DB_PORT"))

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
# -------------------------------------------------------------

def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize database
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS urls (id SERIAL PRIMARY KEY, original_url TEXT NOT NULL, short_code TEXT UNIQUE NOT NULL);')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    original_url = data.get('url')
    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = secrets.token_urlsafe(5)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO urls (original_url, short_code) VALUES (%s, %s)', (original_url, short_code))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"short_url": f"http://localhost:8000/{short_code}"})

@app.route('/<short_code>')
def redirect_to_url(short_code):
    # Try Cache first
    original_url = cache.get(short_code)
    
    if not original_url:
        # Cache miss, check DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT original_url FROM urls WHERE short_code = %s', (short_code,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            original_url = row[0]
            # Set to cache for 10 minutes
            cache.setex(short_code, 600, original_url)
        else:
            return "URL not found", 404

    return redirect(original_url)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
