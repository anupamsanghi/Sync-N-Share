import os, time
import csv
#import clientSync

newlog = {}
oldlog = {}

def modoldlog(operation, content):
	global oldlog
	for key,val in csv.reader(open("filelog.csv")):
		oldlog[key] = val.strip('()')	
	if operation =="add":
		oldlog.update(content)
	if operation =="modify":
		content = content.split(":")
		oldlog[content[0]] = content[1]
	createlogfile() 
	print oldlog

def gettimelog(dirname):
	global newlog
	absdir = os.path.abspath(dirname)
	files = os.listdir(dirname)
	for filename in files:
		absfile = absdir+"/"+filename
		if os.path.isfile(absfile):
			newlog[absfile]=str(os.path.getmtime(absfile))+','+str(os.path.getctime(absfile))
		elif os.path.isdir(absfile):
			gettimelog(absfile)

def createlogfile():
	w = csv.writer(open("filelog.csv", "w"))
	for key, val in oldlog.items():
		w.writerow([key, val])

def getUpdates():
	global oldlog
	global newlog
	print "in getupdates()"
	updatelist = {}
	updatelist["add"] = []
	updatelist["delete"] = []
	updatelist["modify"] = []
	updatelist["rename"] = []
	if oldlog != newlog:
		for key in oldlog.keys():
			if not newlog.has_key(key):
				updatelist["delete"].append(key)
			else:
				if str(oldlog[key]) != str(newlog[key]):
					updatelist["modify"].append(key)
		for key in newlog.keys():
			if not oldlog.has_key(key):
				updatelist["add"].append(key) 
		for addfile in updatelist["add"]:
			for delfile in updatelist["delete"]:
				#print 
				if oldlog[delfile][0] == newlog[addfile][0]:
					updatelist["rename"].append((delfile,addfile))
					updatelist["add"].remove(addfile)
					updatelist["delete"].remove(delfile)
	print updatelist
	return updatelist
def init():
	global oldlog
	directory = "Sync-n-Share"
	if not os.path.isfile("filelog.csv"):
		w = csv.writer(open("filelog.csv", "w"))
		
	else:
		if not oldlog:
			for key,val in csv.reader(open("filelog.csv")):
				oldlog[key] = val.strip('()')	
	gettimelog(directory)
	updatelist = getUpdates()
	#time.sleep(2)
	oldlog = newlog.copy()
	print oldlog
	newlog.clear()
	#time.sleep(2)
	return updatelist
