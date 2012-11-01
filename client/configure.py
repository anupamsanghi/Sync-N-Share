import socket
import sys

if __name__ == "__main__":
	flag = raw_input('New User? (Y/N)')
	print flag
	username = raw_input('Enter the username')
	hostname= socket.gethostname()
	flag1 = False
	if flag =='Y':
		name = raw_input('Enter your name')
		while flag1 == False:
			password = raw_input('Enter the password')
			repassword = raw_input('Re-Enter the password')
			if password != repassword:
				print "passwords donot match!"
				flag1 = False
			else:
				flag1 = True
		data = username+','+name+','+password+','+hostname
	else:
		password = raw_input('Enter the password')
		data = username+','+password+','+hostname
	HOST, PORT = "localhost", 5000
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
	    sock.connect((HOST, PORT))
	    print data
	    sock.send(data)
	    received = sock.recv(1024)
	    if received =='0':
		    print "Invalid username or password"
	    elif received == '1':
		   	 fp=open('userlog','w')
			 fp.write(username+'^'+hostname)
	    else:
		    print "username already exists"
	except:
		print "Unexpected error:", sys.exec_info()[0]
