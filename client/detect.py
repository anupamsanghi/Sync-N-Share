import os, time
import csv
import ast
import copy

newlog = {}
oldlog = {}

def modoldlog(operation, content):
	global oldlog
	print "in modoldlog"
	print oldlog
#	for key,val in csv.reader(open("filelog.csv")):
#		oldlog[key] = val.strip('()')	
	print "oldlog updated"
	print oldlog
	if operation =="add":
		oldlog.update(content)
		print "oldlog in add......................................................................."
		print oldlog
	if operation =="modify":
		content = content.split(":")
		oldlog[content[0]] = content[1]
	if operation =="rename":
		content = content.split('^')
		newentry = ast.literal_eval(content[1])
		oldlog.pop(content[0])
		oldlog.update(newentry)
	if operation =="delete":
		oldlog.pop(content)
	createlogfile() 
	print "modoldlog end.................................................................................."
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
	global oldlog
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
	print oldlog
	print newlog
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
				if oldlog[delfile][0] == newlog[addfile][0]:
					updatelist["rename"].append((delfile,addfile))
					updatelist["add"].remove(addfile)
					updatelist["delete"].remove(delfile)
	print updatelist
	return updatelist
def init():
	global oldlog
	global newlog
	directory = "Sync-n-Share"
	if not os.path.isfile("filelog.csv"):
		w = csv.writer(open("filelog.csv", "w"))
		
	else:
		if not oldlog:
			print "csv read"
			for key,val in csv.reader(open("filelog.csv")):
				oldlog[key] = val.strip('()')	
	print "initial oldlog"
	print oldlog
	gettimelog(directory)
	print "init newlog"
	print newlog
	updatelist = getUpdates()
	#time.sleep(2)
	oldlog = copy.deepcopy(newlog)
	print "init oldlog"
	print oldlog
	newlog.clear()
	#time.sleep(2)
	return updatelist
