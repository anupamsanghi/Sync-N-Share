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
	except:	
		userinfo = configure.init(sock)
	return userinfo

if __name__=="__main__":	
	sock = connectify.createCon()
	userinfo = getUser(sock)
	while 1:
		print "in loop"
		updatelist = detect.init()
		count = countUpdates(updatelist) 
		sock.send('2'+userinfo)
		content = sock.recv(1024)
		print "count value : "+content
		if content!= '0':
			for i in range(0,int(content)):
				sock.send('3'+userinfo)
				updatelist = updateClient.init(sock, updatelist)
		#print updatelist
		if count > 0:
				print "updating log file"
				detect.createlogfile()
		print updatelist
		count = countUpdates(updatelist) 
		time.sleep(2)
		if count > 0:
			clientSync.init(sock, updatelist)
			#	detect.createlogfile()
		#time.sleep(2)
	connectify.closeCon(sock)
