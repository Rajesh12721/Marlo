# Import Functions
from flask import Flask, request, jsonify, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import csv
import sqlite3
# Flask
app = Flask('__name__')
# SQLAlchemy Setup
basefile = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basefile,'Users.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
# Object
db = SQLAlchemy(app)
ma = Marshmallow(app)
# Assign Datatype
class users(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Firstname = db.Column(db.String(50))
    Lastname = db.Column(db.String(50))
    DOB = db.Column(db.Date)
    Email = db.Column(db.String(50))
    Mobileno = db.Column(db.Integer, unique=True)
    Username = db.Column(db.String(20))
    Password = db.Column(db.String(20))
    Usertype = db.Column(db.String(50))
    # Assign Values to Key
    def __init__ (self,fname,lname,dob,email,mno,uname,pwd,user):
        self.Firstname = fname
        self.Lastname = lname
        self.DOB = dob
        self.Email = email
        self.Mobileno = mno
        self.Username = uname
        self.Password = pwd
        self.Usertype = user
    # Database Creation
    with app.app_context():
        db.create_all()
# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('ID','Firstname','Lastname','Email','Mobileno','Username','Password','Usertype')
user_data = UserSchema(many=True)
# Index Page
@app.route('/')
def index():
    return '<h1>Welcome!</h1>'
# Login Page API
@app.route('/login',methods=['POST'])
def loginuser():
    Uname = request.form['uname']
    Pwd = request.form['pwd']
    return '<h1>Welcome %s</h1>' % Uname
# Register API
@app.route('/register', methods=['GET'])
def reguser():
    Fname = request.args.get('fname')
    Lname = request.args.get('lname')
    Dob = request.args.get('dob')
    Email = request.args.get('email')
    Mno = request.args.get('mno')
    Uname = request.args.get('uname')
    pwd = request.args.get('pwd')
    user = request.args.get('user')
    return redirect(url_for('index'))
# Database Connection
def query(query, args=(), one=False):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    con.commit()
    con.close()
    return (rv[0] if rv else None) if one else rv
# Upload File API
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save(file.filename)
    # Insert value
    with open(file.filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            query("INSERT INTO products (name, barcode, brand, description, price, available) VALUES (?, ?, ?, ?, ?, ?)", (row['name'], row['barcode'], row['brand'], row['description'], row['price'], row['available']))
    return jsonify({"status": "success"})
# Review API
@app.route('/review', methods=['POST'])
def review():
    data = request.get_json()
    query("INSERT INTO reviews (product_id, review, rating) VALUES (?, ?, ?)", (data['product_id'], data['review'], data['rating']))
    return jsonify({"status": "success"})
# Product API
@app.route('/products', methods=['GET'])
def view_products():
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    products = query(f"SELECT * FROM products ORDER BY (SELECT AVG(rating) FROM reviews WHERE product_id = products.id) DESC LIMIT {per_page} OFFSET {offset}")
    return jsonify(products)
# Main
if __name__ == '__main__':
    app.run(debug=True)