from flask import Flask, redirect, url_for, request, render_template, session
import hashlib
#from datetime import timedelta


from user import User

app = Flask(__name__)

app.secret_key = '''Qp5NWkGtNvAk0Ti1JAiwvuFve6KiZtAvur86xVd9k7LVTXYz4qGoer7n9DXT
j4l26AS3q5cRF6IovlyTwC4N0dSZAKs4uobWNhNuN2NNWANjZDesyKMWItSkGMRUc8XG9j7k8yQnftUB
y5USFesLJ4bgnLl3YVdSq8MNaEmjWOcxjMU8j6N05c9qHyINGerKtiDmnY7U'''

#app.permanent_session_lifetime = timedelta(minutes = 60)

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
			session["user"] = user.mail
			if "r_err" in session:
				session.pop("r_err", None)
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
			if "l_err" in session:
				session.pop("l_err", None)
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


if __name__ == '__main__':
	app.run(debug = True)
