from socket import * 
from threading import *
import thread
import authenticate
import updates
import updateServer
import connectifyDB

def handler(clientsock, addr):
	db = connectifyDB.getDB()
	request = clientsock.recv(512)
	print request
	requestid = request[0]
	request = request[1:]
	print requestid
	if requestid == '1':
		response = authenticate.auth(request,db) #request = 1username,password
	elif requestid == '2':
		response = updates.getCount(request,db) # request = 2username
	elif requestid == '3':
		response = updates.getUpdate(request,db) #request = 3username
	elif requestid == '4':
		response = updates.getFileContent(request,db) #request = 4username^filename
	elif requestid == '5':
		response = updateServer.update(request,db) #request = 5username^userpc^operation^filename
	elif requestid == '6':
		response = updateServer.sync(request,db) #request = 6username^userpc^filename^diff
	clientsock.send(response)

if __name__=="__main__": 
       HOST = '0.0.0.0'
       PORT = 5050
       BUFSIZ = 1024
       ADDR = (HOST, PORT)
       serversock = socket(AF_INET, SOCK_STREAM)
       serversock.bind(ADDR)
       serversock.listen(5)
       while 1:
   	    print 'waiting for connection'
   	    clientsock, addr = serversock.accept()
   	    print 'connected from:', addr
 	    thread.start_new_thread(handler,( clientsock, addr))
