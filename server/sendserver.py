import socket
import os
import MySQLdb
if __name__ == "__main__":
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("", 5000))	
	server_socket.listen(5)
	print "TCPServer Waiting for client on port 5000"
	client_socket, address = server_socket.accept()
	print "I got a connection from ", address
	print client_socket
	data = client_socket.recv(512)
	print data
	server.serve_forever()
