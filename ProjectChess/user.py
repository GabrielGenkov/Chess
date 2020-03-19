from database import DB

class User:
	def __init__(self, id, username, mail, password):
		self.id = id
		self.username = username
		self.mail = mail
		self.password = password

	def create(self):
		with DB() as db:  
			values = (self.username, self.mail, self.password)
			check = db.execute('''
				SELECT mail FROM Users WHERE mail=?''', 
				(self.mail,)).fetchone()
			if check:
				return None
			db.execute('''
				INSERT INTO Users (username, mail, password)
				VALUES (?, ?, ?)''', values)
			return self

	@staticmethod
	def load(mail, password):
		with DB() as db:
			values = db.execute("SELECT * from Users WHERE mail = ? AND password = ? ", (mail,password,)).fetchone()
		if not values:
			return None
		return User(*values)
		
	@staticmethod
	def load1(mail):
		with DB() as db:
			values = db.execute("SELECT * from Users WHERE mail = ?", (mail,)).fetchone()
		if not values:
			return None
		return User(*values)
