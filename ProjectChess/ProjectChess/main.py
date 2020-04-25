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


@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		error = None
		if "r_err" in session:
			error = session["r_err"]
		return render_template('signin.html', error = error)
	elif request.method == 'POST':
		values = (
			None,
			request.form['username'],
			request.form['mail'],
			hashlib.sha1((request.form['password'] + "itscoronatime").encode('utf-8')).hexdigest()
		)
		user = User(*values).create()
		if user:
			user = User.load1(user.mail)
			session["user"] = user.mail
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
			session["user"] = user.mail
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
		user = User.load1(session["user"])
	return render_template('index.html',user = user)

@app.route('/logout')
def logout():
	session.pop("user", None)
	return redirect('/')

'''@app.route('/<int:id>')
def game(id):
	curr_usr = None
	if "user" in session:
		curr_usr = User.load1(session["user"])
		host = User.load2(id)
		if host:
			return render_template('room.html', host = host, curr_usr = curr_usr)
	return redirect('/')'''

@app.route("/default/<int:id>")
def chatroom(id):
	global users
	if not "user" in session:
		return redirect('/')
	if not User.load2(id):
		return redirect('/')
	if User.load1(session["user"]).mail != User.load2(id).mail and str(id) not in users:
		return redirect('/')
	if User.load1(session["user"]).mail == User.load2(id).mail and str(id) not in users:
		users[str(id)] = list()
	return render_template("room.html", user=User.load1(session["user"]), host = User.load2(id))
	
@socketio.on("send message")
def message(data):
    channel = data['channel']
    message = data['message']
    emit('broadcast message', message, channel)

@socketio.on('join')
def on_join(data):
	global users
	username = data['username']
	channel = data['channel']
	if str(channel) in users:
		if data['mail'] not in users[str(channel)]:
			users[str(channel)].append(data['mail'])
			emit('broadcast users', users[str(channel)], channel)
		print(users[str(channel)])
	join_room(channel)
	emit('broadcast message', username + ' has connected!', channel)

@socketio.on('leave')
def on_leave(data):
	username = data['username']
	channel = data['channel']
	if str(channel) in users:
		if data['mail'] in users[str(channel)]:
			users[str(channel)].remove(data['mail'])
	leave_room(channel)
	emit('broadcast message', username + ' has left the room.', channel)


if __name__ == '__main__':
	#app.run(debug = True)
	socketio.run(app, debug = True)
