from mysql_db import mysql_db

def GET_unknown():
	mySQL = mysql_db()
	try:
		print("DB error")
		info = mySQL.getData("select 1;")		
		return info
		
	except:		
		return "Weight data is ok"
