from Tool import app, db, socketio
from Tool.models import User, Clan, Message, Case, ClueAccess
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import join_room, emit, send, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
from datetime import datetime 
import stripe


stripe.api_key = app.config['STRIPE_SECRET_KEY']

# Utility to generate unique clan codes
def generate_clan_code(length=6):
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


@app.route('/play') 
def play():
    cases = Case.query.all()
    return render_template('play.html', cases = cases)


# Single-player play route
@app.route('/play/single/<cid>')
def play_single(cid):
    if not session.get(f'vid_{cid}', False):
        return redirect(url_for('vid_single', cid = cid))  
    case = db.session.get(Case, cid)
    return render_template('play_single.html', case=case)

# Single-player video view route
@app.route('/vid/single/<cid>')
def vid_single(cid):
    case = db.session.get(Case, cid)
    session[f'vid_{cid}'] = True  # Session tracking to avoid repeated redirects
    return render_template('video_player_single.html', case=case)



@app.route('/play/multi/<clan_code>')
def play_multi(clan_code):
    if not session.get(f'vid_{clan_code}', False):
        return redirect(url_for('vid_multi', clan_code = clan_code))
    clan = Clan.query.filter_by(room_code = clan_code).first()      
    print('clm', clan.messages)
    return render_template('play_multi.html', clan = clan, room = clan)


@app.route('/vid/multi/<clan_code>')
def vid_multi(clan_code):
    clan = Clan.query.filter_by(room_code = clan_code).first()
    case = db.session.get(Case, clan.case_id)
    session[f'vid_{clan_code}'] = True
    return render_template('video_player_multi.html', clan = clan, case = case)

@app.route('/clans/<cid>')
def clans(cid):
    clans = Clan.query.filter_by(case_id = cid).all()
    print(clans)
    clans_clean = []
    for clan in clans:
        clans_clean.append({
            'id' : clan.id,
            'name' : clan.name,
            'members' : f'{len(clan.users)}/{clan.max_users}',
            'code' : clan.room_code
        })
    return render_template('clans.html', cid = cid, clans = clans, clans_clean = clans_clean)


@app.route('/create-clan/<cid>')
def create_clan(cid):
    return render_template('create_clan.html', cid = cid)

@app.route('/_add_cases')
def _add_cases():
    cases = [
        {
            "title": "HAUNTED HOUSE HANG UP",
            "description": "nkmnksjg igighnlu fgbbghjhbkjivubknkiuyufibnkmnksjg igighnlu fgbbghjhbkjivubknkiuyufibnkmnksjg igighnlu fgbbghjhbkjivubknkiuyufibnkmnksjg igighnlu",
            "answer": "test ans",  # Placeholder for answers
            "clues": ["test cl1", "test cl2", "test cl3", "test cl4", "test cl5"],
            "cover_image": "../static/img/case button/1.png",
            "background_image": "../static/img/case bg/1.png",
            "reward": 1000,
            "locked": False,
            "video": "img/case vid/sample.mp4"
        },
        {
            "title": "COMING SOON",
            "description": "Something has happened in crystal cave again! Mayor Jones is under attack by a poltergeist in his own home, and the only ones who can help him are Scooby and the gang. Could you help Mayor Jones before it's too late?",
            "answer": "",  # Placeholder for answers
            "clues": None,
            "cover_image": "../static/img/case button/2.png",
            "background_image": "../static/img/case bg/2.png",
            "reward": 1000,
            "locked": True,
            "video": None
        },
        {
            "title": "COMING SOON",
            "description": "The gang investigate an old abandoned amusement park, when it suddenly jumps into life, and the mysterious robot that seems to have taken it over. Could you help Scooby Doo and the gang to fight against the tank of robots?",
            "answer": "",  # Placeholder for answers
            "clues": None,
            "cover_image": "../static/img/case button/3.png",
            "background_image": "../static/img/case bg/3.png",
            "reward": 1000,
            "locked": True,
            "video": None
        }
    ]

    # Add each case to the database
    for case_data in cases:
        new_case = Case(
            title=case_data['title'],
            description=case_data['description'],
            answer=case_data['answer'],
            clues=case_data['clues'],
            cover_image=case_data['cover_image'],
            background_image=case_data['background_image'],
            reward=case_data['reward'],
            locked=case_data['locked'],
            video=case_data['video']
        )
        db.session.add(new_case)

    db.session.commit()
    return jsonify({"message": "Cases added successfully"})


@app.route('/create_clan/<int:case_id>', methods=['POST'])
@login_required
def create_clan_post(case_id):
    name = request.form['name']
    code = request.form['code']
    max_n = request.form['max_n']
    new_clan = Clan(name = name, max_users = max_n, room_code = code, case_id = case_id)
    db.session.add(new_clan)
    new_clan.users.append(current_user)
    db.session.commit()
    return redirect(url_for('clan', clan_code=code))

@app.route('/join_clan/<clan_code>', methods=['POST'])
@login_required
def join_clan(clan_code):
    clan = Clan.query.filter_by(room_code=clan_code).first()
    if not clan:
        flash('Clan not found', 'error')
        return redirect(url_for('clans', cid = 1))

    if current_user in clan.users:  
        return redirect(url_for('clan', clan_code=clan_code))

    clan.users.append(current_user)
    db.session.commit()
    return redirect(url_for('clan', clan_code=clan_code))
    

@app.route('/clan/<clan_code>')
@login_required
def clan(clan_code):
    return redirect(url_for('play_multi', clan_code = clan_code))

# SocketIO Events for Chat
@socketio.on('join')
def handle_join(data):
    clan_code = data['room']
    join_room(clan_code)
    send(f"{current_user.username} has entered the clan.", to=clan_code)

@socketio.on('message')
def handle_message(data):
    print('data ' , data)
    clan_code = data['room']
    content = data['message']
    message = Message(content=content, user_id=current_user.id, room_id=Clan.query.filter_by(room_code=clan_code).first().id)
    print('msg', message)
    db.session.add(message)
    db.session.commit()
    emit('message', {'user': current_user.username, 'message': content}, to=clan_code)

@socketio.on('leave')
def handle_leave(data):
    clan_code = data['room']
    leave_room(clan_code)
    send(f"{current_user.username} has left the clan.", to=clan_code)


@app.route('/check-clan-name', methods=['POST'])
def check_clan_name():
    data = request.get_json()
    clan_name = data.get('name')

    # Check if clan name exists in the database
    existing_clan = Clan.query.filter_by(name=clan_name).first()

    if existing_clan or clan_name == 'test':
        return jsonify({'message': 'Clan name is not available.'})
    else:
        return jsonify({'message': 'Clan name is available.'})


# Route to check clan code availability
@app.route('/check-clan-code', methods=['POST'])
def check_clan_code():
    data = request.get_json()
    clan_code = (data.get('code'))

    # Check if clan code exists in the database
    existing_clan = Clan.query.filter_by(room_code=clan_code).first()

    if existing_clan or clan_code == '111':
        return jsonify({'message': 'Clan code is already taken.'})
    else:
        return jsonify({'message': 'Clan code is available.'})
    



@app.route('/get-clue', methods=['POST'])
@login_required
def get_clue():
    case_id = request.form.get('case_id')
    clue_no = int(request.form.get('clue_no'))
    clan_code = (request.form.get('clue_no' , None))



    # Fetch the case and clues
    case = db.session.get(Case, case_id)
    clues = case.clues
    if clue_no <= len(clues):
        clue = clues[clue_no - 1]
    else:
        return jsonify({'error': 'Clue not found'}), 404

    # Check if clue has been accessed by this user for this case and clue number
    existing_access = ClueAccess.query.filter_by(user_id=current_user.id, case_id=case_id, clue_no=clue_no).first()

    # Deduct gems only if it's the user's first time accessing this clue
    if not existing_access:
        # Deduct gems if clue number is >= 4
        if clue_no >= 4:
            if current_user.gems < 1000:
                return jsonify({'error': 'Insufficient Aura'}), 404
            current_user.gems -= 1000
            db.session.commit()

        # Record the clue access
        new_access = ClueAccess(user_id=current_user.id, case_id=case_id, clue_no=clue_no)
        db.session.add(new_access)
        if (clan_code):
            clan = Clan.query.filter_by(room_code = clan_code)
            for user in clan.users:
                new_access = ClueAccess(user_id=user.id, case_id=case_id, clue_no=clue_no)
                db.session.add(new_access)
        db.session.commit()

    return jsonify({'clue': clue}), 200
   
@app.route('/check-ans', methods=['POST'])
@login_required
def check_answer():
    data = request.get_json()
    case_id = data.get('case_id')
    user_answer = data.get('answer')

    # Retrieve the case from the database
    case = Case.query.get(case_id)
    if not case:
        return jsonify({"status": "error", "message": "Case not found."}), 404

    # Check if the user's answer matches the case answer
    if user_answer.strip().lower() == case.answer.strip().lower():
        # Reward user if the answer is correct (optional)
        reward = case.reward
        current_user.gems += reward
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Correct answer!", "reward": reward})
    else:
        return jsonify({"status": "error", "message": "Incorrect answer. Try again!"}), 200


if __name__ == '__main__':
    socketio.run(app, debug=True)
