from socket import * 
from threading import *
import thread
import fileOperation

def handler(clientsock, addr):
	request = clientsock.recv(512)
	print request
	requestid = request[0]
	request = request[1:]
	print requestid
	if requestid == '1':
		response = fileOperation.read(request)
	elif requestid == '2':
		response = fileOperation.write(request)
	elif requestid == '3':
		response = fileOperation.rename(request)
	clientsock.send(response)

if __name__=="__main__": 
       HOST = '0.0.0.0'
       PORT = 4000
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
