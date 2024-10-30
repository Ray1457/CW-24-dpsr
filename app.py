from Tool import app, db, socketio
from Tool.models import User, Room, Message, Case
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import join_room, emit, send, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
from datetime import datetime 

# Utility to generate unique room codes
def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        # Create a new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('profile'))
    
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        
        flash('Login failed. Check your email and password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/')
def home():
    if (current_user.is_authenticated):
        flash(f'Logged in as {current_user.username}', 'error')
    return render_template('index.html')



@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if request.method == 'POST':
        data = request.json
        print(data)
        user_id = data.get('id')  # Assuming 'id' is sent to identify the user
        user = db.session.get(User, user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update user profile information
        user.name = data.get('name', user.name)
        user.age = data.get('age', user.age)
        user.height = data.get('height', user.height)
        dob_str = data.get('dob')
        user.dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else user.dob
        user.about = data.get('about', user.about)

        # Save changes
        db.session.commit()

        return jsonify({"message": "Profile updated successfully"}), 200

    return render_template('profile.html', user = current_user)  


@app.route('/create_room/<int:case_id>', methods=['POST'])
@login_required
def create_room(case_id):
    room_code = generate_room_code()
    new_room = Room(room_code=room_code, case_id=case_id)
    db.session.add(new_room)
    db.session.commit()
    return redirect(url_for('room', room_code=room_code))

@app.route('/join_room/<room_code>', methods=['GET', 'POST'])
@login_required
def join_room_view(room_code):
    room = Room.query.filter_by(room_code=room_code).first()
    if not room:
        flash('Room not found', 'error')
        return redirect(url_for('home'))

   
    room.users.append(current_user)
    db.session.commit()
    return redirect(url_for('room', room_code=room_code))
    

@app.route('/room/<room_code>')
@login_required
def room(room_code):
    room = Room.query.filter_by(room_code=room_code).first_or_404()
    return render_template('room.html', room=room, user=current_user)

# SocketIO Events for Chat
@socketio.on('join')
def handle_join(data):
    room_code = data['room']
    join_room(room_code)
    send(f"{current_user.username} has entered the room.", to=room_code)

@socketio.on('message')
def handle_message(data):
    room_code = data['room']
    content = data['message']
    message = Message(content=content, user_id=current_user.id, room_id=Room.query.filter_by(room_code=room_code).first().id)
    db.session.add(message)
    db.session.commit()
    emit('message', {'user': current_user.username, 'message': content}, to=room_code)

@socketio.on('leave')
def handle_leave(data):
    room_code = data['room']
    leave_room(room_code)
    send(f"{current_user.username} has left the room.", to=room_code)

# Signaling for WebRTC Voice Chat (Basic Implementation)
@socketio.on('webrtc_signal')
def webrtc_signal(data):
    emit('webrtc_signal', data, to=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
