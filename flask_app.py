from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'luacraft.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            track TEXT NOT NULL,
            lesson_index INTEGER NOT NULL,
            UNIQUE(user_id, track)
        )
    ''')
    conn.commit()
    conn.close()

def get_progress(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT track, lesson_index FROM progress WHERE user_id = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return {track: idx for track, idx in rows}

def save_progress(user_id, track, lesson_index):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO progress (user_id, track, lesson_index) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, track) 
        DO UPDATE SET lesson_index = ?
    ''', (user_id, track, lesson_index, lesson_index))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(__file__), 'luacraft.html')

@app.route('/api/progress', methods=['GET'])
def api_get_progress():
    user_id = request.args.get('user_id', 'default_user')
    return jsonify(get_progress(user_id))

@app.route('/api/progress', methods=['POST'])
def api_save_progress():
    data = request.json
    save_progress(data.get('user_id', 'default_user'), data.get('track', 'lua'), data.get('lesson_index', 0))
    return jsonify({'status': 'ok'})

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.dirname(__file__), filename)

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))