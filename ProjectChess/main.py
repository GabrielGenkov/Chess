from flask import Flask, redirect, url_for, request, render_template, session
from datetime import timedelta


from user import User

app = Flask(__name__)

app.secret_key = '''Qp5NWkGtNvAk0Ti1JAiwvuFve6KiZtAvur86xVd9k7LVTXYz4qGoer7n9DXT
j4l26AS3q5cRF6IovlyTwC4N0dSZAKs4uobWNhNuN2NNWANjZDesyKMWItSkGMRUc8XG9j7k8yQnftUB
y5USFesLJ4bgnLl3YVdSq8MNaEmjWOcxjMU8j6N05c9qHyINGerKtiDmnY7U'''

app.permanent_session_lifetime = timedelta(minutes = 60)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('signin.html')
	elif request.method == 'POST':
		session.permanent = True
		values = (
			None,
			request.form['username'],
			request.form['mail'],
			request.form['password']
		)
		user = User(*values).create()
		if user:
			session["user"] = user.mail
		return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		mail = request.form['mail']
		password = request.form['password']
		user = User.load(mail, password)
		if user:
			session["user"] = user.mail
	return redirect('/')

@app.route('/')
def main():
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
