import socket
import sys
import time
if __name__=="__main__":
	HOST, PORT = "localhost", 5000
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	while 1:
		string="hi"
		sock.send(string)
		#received = sock.recv(1024)
		#print received
		time.sleep(2)
	sock.close()
