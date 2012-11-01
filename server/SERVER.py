from socket import * 
from threading import *
import thread
import MySQLdb
import authenticate
import updates
import updateServer
import time

def handler(clientsock,addr):
	data = clientsock.recv(512)
	clientsock.send('1') 
	if data == '0':		
		authenticate.auth(clientsock)
	data1 = clientsock.recv(BUFSIZ)
	username = (data1.split('^'))[0]
	print username
	db = MySQLdb.connect( user="root", unix_socket="/opt/lampp/var/mysql/mysql.sock",passwd="", host="localhost",db="os_minor")
	cur = db.cursor() 
	while 1:
		print "in loop"
		updates.getUpdates(username, db,clientsock)
		count = clientsock.recv(BUFSIZ)
		db.commit()
		clientsock.send('1')
		time.sleep(2)
		print "val"+count
		for i in range(0,int(count)):updateServer.update(db, clientsock)
		print "out"
		time.sleep(2)
        clientsock.close()
if __name__=="__main__": 
       HOST = 'localhost'
       PORT = 5000
       BUFSIZ = 1024
       ADDR = (HOST, PORT)
       serversock = socket(AF_INET, SOCK_STREAM)
       serversock.bind(ADDR)
       serversock.listen(5)

       while 1:
             print 'waiting for connection'
             clientsock, addr = serversock.accept()
             print 'connected from:', addr
             thread.start_new_thread(handler, (clientsock, addr))
