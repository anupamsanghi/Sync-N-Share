import MySQLdb

def getDB():
	db = MySQLdb.connect( user="root", unix_socket="/opt/lampp/var/mysql/mysql.sock",passwd="", host="X.X.X.X",db="os_minor")
	return db
