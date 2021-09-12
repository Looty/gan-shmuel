from mysql_db import mysql_db

def GET_unknown():
	mySQL = mysql_db()
	try:
		print("DB error")
		info = mySQL.getData("SELECT distinct id FROM containers WHERE weight IS NULL")		
		return '\n'.join(map(str,info))
		
	except:		
		return "Weight data is ok"



