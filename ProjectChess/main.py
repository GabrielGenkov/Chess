import os
import hashlib
from flask import Flask, redirect, url_for, request, render_template, session
from flask_socketio import SocketIO, join_room, leave_room, emit, send

#from datetime import timedelta

from user import User

app = Flask(__name__)

app.secret_key = '''Qp5NWkGtNvAk0Ti1JAiwvuFve6KiZtAvur86xVd9k7LVTXYz4qGoer7n9DXT
j4l26AS3q5cRF6IovlyTwC4N0dSZAKs4uobWNhNuN2NNWANjZDesyKMWItSkGMRUc8XG9j7k8yQnftUB
y5USFesLJ4bgnLl3YVdSq8MNaEmjWOcxjMU8j6N05c9qHyINGerKtiDmnY7U'''

app.config['SECRET_KEY'] = 'lrgnieijnWI;Evjwn;LH;EVbWKEVJNWIVHUIOihVNO'
socketio = SocketIO(app)

#app.permanent_session_lifetime = timedelta(minutes = 60)

users = dict()
positions = dict()
histories = dict()
modes = dict()
modes['default'] = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
modes['horde'] = "rnbqkbnr/pppppppp/8/1PP2PP1/PPPPPPPP/PPPPPPPP/PPPPPPPP/PPPKPPPP w kq - 0 1"
modes['DickTrap'] = "rppppppr/pnbqkbnp/8/8/8/8/PNBQKBNP/RPPPPPPR w - - 0 1"
modes['Sandwich'] = "pppppppp/rnbqkbnr/pppppppp/8/8/PPPPPPPP/RNBQKBNR/PPPPPPPP w KQkq - 0 1"


@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		error = None
		if "r_err" in session:
			error = session["r_err"]
		return render_template('signin.html', error = error)
	elif request.method == 'POST':
		if len(request.form['password']) < 8:
			session["r_err"] = "Too short password!!"
			return redirect('/register')
		values = (
			None,
			request.form['username'],
			request.form['mail'],
			hashlib.sha1((request.form['password'] + "itscoronatime").encode('utf-8')).hexdigest()
		)
		user = User(*values).create()
		if user:
			user = User.load1(user.mail)
			session["user"] = user.id
			return redirect('/')
		session["r_err"] = "This accaunt already exists!!"
		return redirect('/register')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		error = None
		if "l_err" in session:
			error = session["l_err"]
		return render_template('login.html', error = error)
	elif request.method == 'POST':
		mail = request.form['mail']
		password = hashlib.sha1((request.form['password'] + "itscoronatime").encode('utf-8')).hexdigest()
		user = User.load(mail, password)
		if user:
			session["user"] = user.id
			return redirect('/')
		session["l_err"] = "Acccaunt with that email and password doesn't exists!!"
		return redirect('/login')

@app.route('/')
def main():
	if "r_err" in session:
		session.pop("r_err", None)
	if "l_err" in session:
		session.pop("l_err", None)
	user = None
	if "user" in session:
		user = User.load2(session["user"])
	return render_template('index.html',user = user)

@app.route('/logout')
def logout():
	session.pop("user", None)
	return redirect('/')

@app.route("/<mode>/<int:id>")
def chatroom(mode,id):
	global users
	global positions
	global histories
	global modes
	second_player = False
	if not "user" in session:
		return redirect('/')
	if not User.load2(id):
		return redirect('/')
	if session["user"] != id and mode + str(id) not in users:
		return redirect('/')
	if session["user"] == id and mode + str(id) not in users:
		users[mode + str(id)] = list()
		positions[mode + str(id)] = modes[mode]
		histories[mode + str(id)] = ""
	if session["user"] != id and mode + str(id) in users:
		if(len(users[mode + str(id)]) == 1):
			second_player = True
		if(len(users[mode + str(id)]) >= 2 and users[mode + str(id)][1] == session["user"]):
			second_player = True
	return render_template("room.html", user=User.load2(session["user"]), host = User.load2(id), position = positions[mode + str(id)], history = histories[mode + str(id)] ,second_player = second_player, mode = mode)
	
@socketio.on("send message")
def message(data):
    channel = data['channel']
    message = data['message']
    user = data['user']
    emit('broadcast message', user + " : " + message, channel)

@socketio.on('join')
def on_join(data):
	global users
	channel = data['channel']
	username = User.load2(data['id']).username
	if str(channel) in users:
		if data['id'] not in users[str(channel)]:
			users[str(channel)].append(data['id'])
		print(users[str(channel)])
	join_room(channel)
	emit('broadcast message', username + ' has connected!', channel)

@socketio.on('leave')
def on_leave(data):
	channel = data['channel']
	username = User.load2(data['id']).username
	if str(channel) in users:
		if data['id'] in users[str(channel)]:
			users[str(channel)].remove(data['id'])
	leave_room(channel)
	emit('broadcast message', username + ' has left the room.', channel)

@socketio.on("send position")
def update_position(data):
	position = data['position']
	channel = data['channel']
	history = data['history']
	histories[str(channel)] = history
	positions[str(channel)] = position
	emit('broadcast table', history, channel)

if __name__ == '__main__':
	#app.run(debug = True)
	socketio.run(app, debug = True)
