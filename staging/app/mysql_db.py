import mysql.connector

class mysql_db(object):
	def __init__(self):
		self.db_user = "root"
		self.db_pass = "123456"
		self.db_host = "db_wg"
		self.db_name = "db"
		self.connections = None

	def doConnect(self):
		if self.connections is None:
			self.connections = mysql.connector.connect(user='root', password='123456', host='mysql_db', database='db')
		return self.connections

	def getData(self,querry):
		connected = self.doConnect()
		data = []
		cur = connected.cursor(dictionary=True, buffered=True)
		res = cur.execute(querry)
		