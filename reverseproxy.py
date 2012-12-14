from socket import * 
from threading import *
import thread
servers =[{"host":"localhost", "port" :5050, "requests" : 0},{"host":"localhost", "port" :8080, "requests" : 0}]
def handler(clientsock, addr):
	flagserver = 0
	global servers
	while 1:
		request = clientsock.recv(512)
		print "request: "+request
		sock = socket(AF_INET, SOCK_STREAM)
		min_requests = servers[0]['requests']
		for i in range (0,len(servers)):
			if min_requests > servers[i]['requests']:
				min_requests = servers[i]['requests']
				flagserver = i
		sock.connect((servers[flagserver]['host'], servers[flagserver]['port']))
		servers[flagserver]['requests'] +=1
		sock.send(request)
		response = sock.recv(512) 
		print "response: "+response
		servers[flagserver]['requests'] -=1
		clientsock.send(response)

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
