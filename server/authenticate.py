import MySQLdb
def auth(sock):
	result = 0
	attempt = 1
	while result == 0 and attempt <=3:
	    	data = sock.recv(512)
		if not data: 
			sock.close()
			break				
		print data  
	    	db = MySQLdb.connect( user="root", unix_socket="/opt/lampp/var/mysql/mysql.sock",passwd="", host="localhost",db="os_minor")
		cur = db.cursor() 
		userinfo = data.split(',')
		cur.execute("SELECT * FROM user_info WHERE username = '"+userinfo[0]+"' and password = '"+userinfo[1]+"'")
		resultset = cur.fetchall()
		result = len(resultset)
		if result == 0:
			sock.send('0') 
		else:
			sock.send('1')
		attempt+=1
