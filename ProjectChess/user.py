from database import DB

class User:
	def __init__(self, id, username, mail, password, points = 0):
		self.id = id
		self.username = username
		self.mail = mail
		self.password = password
		self.points = points

	def create(self):
		with DB() as db:  
			values = (self.username, self.mail, self.password, 0)
			check = db.execute('''
				SELECT mail FROM Users WHERE mail=?''', 
				(self.mail,)).fetchone()
			if check:
				return None
			db.execute('''
				INSERT INTO Users (username, mail, password, points)
				VALUES (?, ?, ?, ?)''', values)
			return self
			
	def addPoints(self, points):
		with DB() as db:
			check = db.execute('''
				SELECT mail FROM Users WHERE mail=?''', 
				(self.mail,)).fetchone()
			if not check:
				return None
			if points == 0:
				return None
			values = (self.points + points, self.id)
			db.execute('UPDATE Users SET points = ? WHERE id = ?', values)
			return self

	@staticmethod
	def all():
		with DB() as db:
			rows = db.execute('SELECT * FROM Users WHERE points > 0 ORDER BY points DESC').fetchall()
			return [User(*row) for row in rows]

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
	
	@staticmethod
	def load2(id):
		with DB() as db:
			values = db.execute("SELECT * from Users WHERE id = ?", (id,)).fetchone()
		if not values:
			return None
		return User(*values)
		
	
