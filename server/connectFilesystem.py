import socket
import sys

def createCon():
	HOST, PORT = "X.X.X.X", 4000
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	return sock

def getResponse(data, sock):
	print "connectify:"+data
	sock.send(data)
	received = sock.recv(1024)
	print "received :"+received
	return received

def closeCon(sock):
	print "Exiting..."
	#sock.close()
	#sys.exit()
