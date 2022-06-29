from hashlib import md5
from flask import Flask,render_template, request, session, redirect, url_for, flash
from flask_paginate import Pagination, get_page_args
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'AHjkaIllq!@$%^&*()'
mysql = MySQL(app)

app.config['MYSQL_HOST'] = 'us-cdbr-east-05.cleardb.net'
app.config['MYSQL_USER'] = 'be59ae2d82a4ee'
app.config['MYSQL_PASSWORD'] = '4b277e32'
app.config['MYSQL_DB'] = 'heroku_a91c363318c38ae'


# get_user
def get_users(offset=0, per_page=5):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_user LIMIT %s, %s', (offset, per_page))
    return cursor.fetchall()

# create tables
def create_tables():
    conn = MySQLdb.connect(host='us-cdbr-east-05.cleardb.net', user='be59ae2d82a4ee', passwd='4b277e32', db='heroku_a91c363318c38ae')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE `tbl_user` (`id_user` int(11) NOT NULL AUTO_INCREMENT,`nama` varchar(50) NOT NULL,`username` varchar(50) NOT NULL,`password` varchar(50) NOT NULL,`email` varchar(50) NOT NULL,`address` varchar(50) NOT NULL,PRIMARY KEY (`id_user`)) ENGINE=InnoDB DEFAULT CHARSET=latin1")
    conn.commit()
    conn.close()

# get total user
def get_total_user():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_user')
    return cursor.rowcount

@app.route("/")
def homepage():
    if 'username' in session:
        page, per_page, offset = get_page_args(page_parameter='page',per_page_parameter='per_page')
        total = get_total_user()
        pagination_users = get_users(offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap3')
        return render_template('index.html',user=pagination_users,page=page,per_page=10,pagination=pagination)
    else:
        flash('Anda harus login terlebih dahulu')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data
        username = request.form['username']
        password = request.form['password']
        # get user by username
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_user WHERE username = %s', [username])
        # fetch one row
        user = cursor.fetchone()
        # if user not found
        if user is None:
            flash('Username tidak ditemukan')
            return redirect(url_for('login'))
        # if user found
        if user['password'] != md5(password.encode('utf-8')).hexdigest():
            flash('Password salah')
            return redirect(url_for('login'))
        # if user found and password is correct
        session['logged_in'] = True
        session['nama'] = user['nama']
        session['address'] = user['address']
        session['username'] = user['username']
        session['id_user'] = user['id_user']
        flash('Selamat datang ' + session['nama'])
        return redirect(url_for('homepage'))
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    if 'username' not in session:
        if request.method == 'POST' and 'nama' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form:
            nama = request.form['nama']
            username = request.form['username']
            password = md5(request.form['password'].encode('utf-8')).hexdigest()
            email = request.form['email']
            address = request.form['address']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM tbl_user WHERE username = % s', (username, ))
            account = cursor.fetchone()
            if account:
                flash('Account already exists !')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address !')
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash('name must contain only characters and numbers !')
            else:
                cursor.execute('INSERT INTO tbl_user VALUES (NULL, % s, % s, % s, % s, % s )', (nama, username, password, email, address ))
                mysql.connection.commit()
                flash('You have successfully registered !')
        elif request.method == 'POST':
            flash( 'Please fill out the form !')
        return render_template('register.html')
    if 'logged_in' in session:
        return redirect(url_for('homepage'))
    return render_template('register.html')

@app.route('/add_user',methods=['POST'])
def add_user():
    if 'username' in session:
        if request.method == 'POST':
            nama = request.form['nama']
            username = request.form['username']
            password = md5(request.form['password'].encode('utf-8')).hexdigest()
            email = request.form['email']
            address = request.form['address']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # account = cursor.fetchone()
            cursor.execute('INSERT INTO tbl_user VALUES (NULL, % s, % s, % s, % s, % s)', (nama, username, password, email, address))
            mysql.connection.commit()
            flash(message = 'User berhasil ditambahkan')
        elif request.method == 'POST':
            flash('Isi form dengan benar !')
        return redirect(url_for('homepage'))
    else :
        flash('Anda harus login terlebih dahulu')
        return redirect(url_for('login'))

# Create Search Function
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        user = request.form['user']
        # search by nama, address dan email
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_user WHERE nama LIKE %s OR address LIKE %s OR email LIKE %s', ('%'+user+'%', '%'+user+'%', '%'+user+'%'))
        users = cursor.fetchall()
        # all in the search box will return all the tuples
        if len(users) == 0 and user == 'all':
            cursor.execute('SELECT * FROM tbl_user')
            users = cursor.fetchall()
        return render_template('search.html', users=users)
    else:
        return redirect(url_for('homepage'))
    
# hapus data users
@app.route("/delete_user", methods =['GET', 'POST'])
def delete_user():
    if 'username' in session:
        if request.method == 'POST' and 'id_user' in request.form:
            id_user = request.form['id_user']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM tbl_user WHERE id_user = % s', (id_user, ))
            mysql.connection.commit()
            flash('user berhasil dihapus')
            return redirect(url_for('homepage'))
        return redirect(url_for('homepage'))
    else :
        flash('Anda harus login terlebih dahulu')
        return redirect(url_for('login'))