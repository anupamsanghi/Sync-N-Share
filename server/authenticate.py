import socket
import os
import MySQLdb

if __name__ == "__main__":
	#creating server socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("", 5000))
	server_socket.listen(5)
	print "TCPServer Waiting for client on port 5000"
	client_socket, address = server_socket.accept()
	print "I got a connection from ", address
    	data = client_socket.recv(512)
	print data
   	#client_socket.send(data)    
    	db = MySQLdb.connect( user="root", unix_socket="/opt/lampp/var/mysql/mysql.sock",passwd="", host="localhost",db="os_minor")
	cur = db.cursor() 
	userinfo = data.split(',')
	#print userinfo
	if len(userinfo) == 3:
		cur.execute("SELECT * FROM user_info WHERE username = '"+userinfo[0]+"' and password = '"+userinfo[1]+"'")
		resultset = cur.fetchall()
		if len(resultset) == 0:
			client_socket.send('0') 
		else:
			client_socket.send('1') 
	else:
		cur.execute("INSERT INTO user_info(username,password,name) VALUES('"+userinfo[0]+"', '"+userinfo[2]+"', '"+userinfo[1]+"')")
		cur.close()
		try:
			db.commit()
			client_socket.send('1') 
		except:
			client_socket.send('2')
		db.close()
	server_socket.close()