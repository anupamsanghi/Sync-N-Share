import socket
import sys

def createCon():
	HOST, PORT = "localhost", 5000
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	return sock

def getResponse(data, sock):
	sock.send(data)
	received = sock.recv(1024)
	return received

def closeCon(sock):
	print "Exiting..."
	sock.close()
	sys.exit()
