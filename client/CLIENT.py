import socket
import sys
import time
import os
import configure
import connectify
import userlog
import updateClient
import detect
import clientSync
def countUpdates(updatelist):
	count = len(updatelist["add"])+len(updatelist["modify"])+len(updatelist["rename"])
	if updatelist["delete"]:count +=1	
	#print "val"+str(count)
	return count

def getUser(sock):
	try:
		userinfo = userlog.getInfo()
		received = connectify.getResponse('1',sock)
		if received != '1':connectify.closeCon(sock)
	except:		
		received = connectify.getResponse('0',sock)
		if received != '1':connectify.closeCon(sock)
		userinfo = configure.init(sock)
	return userinfo

if __name__=="__main__":	
	sock = connectify.createCon()
	userinfo = getUser(sock)
	sock.send(userinfo)
	while 1:
		print "in loop"
		updatelist = detect.init()
		count = countUpdates(updatelist) 
		content = sock.recv(1024)
		sock.send('1')
		print "count value : "+content
		if content!= '0':
			for i in range(0,int(content)):
				updatelist = updateClient.init(sock, updatelist)
		#print updatelist
		if count > 0:
				print "updating log file"
				detect.createlogfile()
		print updatelist
		count = countUpdates(updatelist) 
		op = connectify.getResponse(str(count), sock)	
		time.sleep(2)
		if op == '1':
			if count > 0:
				clientSync.init(sock, updatelist)
			#	detect.createlogfile()
		#time.sleep(2)
	connectify.closeCon(sock)