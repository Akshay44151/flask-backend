from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# DB Setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY, user TEXT, product_id INTEGER)')
    conn.commit()
    conn.close()

init_db()

# Add some sample products
def seed_products():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM products')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO products (name, price) VALUES (?, ?)', ('Pen', 10))
        c.execute('INSERT INTO products (name, price) VALUES (?, ?)', ('Book', 50))
        c.execute('INSERT INTO products (name, price) VALUES (?, ?)', ('Bag', 100))
        conn.commit()
    conn.close()

seed_products()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (data['username'], data['password']))
        conn.commit()
        return jsonify({"message": "Signup successful"})
    except:
        return jsonify({"message": "Username already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (data['username'], data['password']))
    if c.fetchone():
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = [{"id": row[0], "name": row[1], "price": row[2]} for row in c.fetchall()]
    return jsonify(products)

@app.route('/cart/<user>', methods=['GET'])
def get_cart(user):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT product_id FROM cart WHERE user=?', (user,))
    product_ids = [row[0] for row in c.fetchall()]
    items = []
    for pid in product_ids:
        c.execute('SELECT id, name, price FROM products WHERE id=?', (pid,))
        row = c.fetchone()
        items.append({"id": row[0], "name": row[1], "price": row[2]})
    return jsonify(items)

@app.route('/cart/add', methods=['POST'])
def add_cart():
    data = request.json
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO cart (user, product_id) VALUES (?, ?)', (data['user'], data['product_id']))
    conn.commit()
    return jsonify({"message": "Added to cart"})

@app.route('/cart/delete', methods=['POST'])
def delete_cart():
    data = request.json
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user=? AND product_id=?', (data['user'], data['product_id']))
    conn.commit()
    return jsonify({"message": "Removed from cart"})
@app.route('/users', methods=['GET'])
def show_users():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT username, password FROM users')
    users = c.fetchall()
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


