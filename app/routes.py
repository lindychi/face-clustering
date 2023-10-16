from app import app, db
from app.models import User
import face_recognition
from flask import request, render_template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            return f"Logged in as {user.username}"
        else:
            return "Invalid username or password"
    return render_template('login.html')