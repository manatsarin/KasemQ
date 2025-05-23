# app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
socketio = SocketIO(app)

DB_FILE = 'queue.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        status TEXT DEFAULT 'waiting',
                        counter INTEGER DEFAULT NULL
                    )''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/staff')
def staff():
    return render_template('staff.html')

@app.route('/display')
def display():
    return render_template('display.html')

@app.route('/get_ticket', methods=['POST'])
def get_ticket():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO queue (status) VALUES ('waiting')")
        conn.commit()
        ticket_id = c.lastrowid
    return jsonify({'ticket': ticket_id})

@app.route('/call_next', methods=['POST'])
def call_next():
    counter = request.json['counter']
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM queue WHERE status='waiting' ORDER BY id LIMIT 1")
        row = c.fetchone()
        if row:
            ticket_id = row[0]
            c.execute("UPDATE queue SET status='called', counter=? WHERE id=?", (counter, ticket_id))
            conn.commit()
            socketio.emit('new_call', {'ticket': ticket_id, 'counter': counter})
            return jsonify({'ticket': ticket_id})
        else:
            return jsonify({'ticket': None})

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
