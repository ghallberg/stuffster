from flask import Flask, render_template, session, request, redirect, url_for, g
from sqlalchemy import *
import flask

import databaseHandler as db

app = Flask(__name__)

@app.route('/')
def stuffster():
    """Start page, redirects to login if there is no cookie for the user"""
    if 'username' in session:
        cats = db.get_categories(session['username'])
        note = db.get_note(session['username'])
        return render_template('template.html', categories = cats, user_note = note)
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Login page, and authorization. Redirects to start page if login info is provided
    and authorized"""
    if db.auth_user(request.form['username'], request.form['password']):
        session['username'] = request.form['username']
        return redirect(url_for('stuffster'))
    else:
        return render_template('login.html')

@app.route('/new_user')
def new_user():
    """Displays the sign up form"""
    return render_template('new_user.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    db.add_user(
        request.form['username'],
        request.form['email'],
        request.form['password']
    )
    return redirect(url_for('stuffster'))

@app.route('/logout')
def logout():
    """remove username from session if it's there"""
    session.pop('username', None)
    return redirect(url_for('stuffster'))

@app.route('/save_note', methods=['POST'])
def save_note():
    if "username" in session:
        db.save_note(request.form['note'], session['username'])
        return redirect(url_for('stuffster'))

    return redirect(url_for('stuffster'))



@app.route('/add_link', methods=['POST'])
def add_link():
    cats = request.form['cats'].split(',')
    cats = [cat.strip() for cat in cats]
    db.add_link(cats,request.form['name'],request.form['address'], session['username'])
    return redirect(url_for('stuffster'))

@app.route('/del_link')
def del_link():
    if not 'username' in session:
        return redirect(url_for('stuffster'))

    db.del_link(request.args.get('linkid',''),request.args.get('cat',''))
    return redirect(url_for('stuffster'))

if __name__ == '__main__':
    app.secret_key = 'fatsug'
    app.run(host = '127.0.0.1', debug = False)

