import os, time
import csv
import clientSync
import socket
import sys

filedict = {}
def gettimelog(dirname):
	global filedict
	absdir = os.path.abspath(dirname)
	files = os.listdir(dirname)
	for filename in files:
		absfile = absdir+"/"+filename
		if os.path.isfile(absfile):
			filedict[absfile]=os.path.getmtime(absfile),os.path.getctime(absfile)
		elif os.path.isdir(absfile):
			gettimelog(absfile)

def createfilelog(log):
	w = csv.writer(open("filelog.csv", "w"))
	for key, (val1, val2) in log.items():
		w.writerow([key, (val1,val2)])
if  __name__ == "__main__":
	added = {}
	deleted = {}
	updated = {}
	renamed = {}	
	filedictold = {}
	for key,val in csv.reader(open("filelog.csv")):
		filedictold[key]=val
	gettimelog("Sync-n-Share")
	while 1:
		
		added.clear()
		deleted.clear()
		updated.clear()
		renamed.clear()
		if filedictold != filedict:
			for key in filedictold.keys():
				if (not filedict.has_key(key)):
					deleted[key] = filedictold[key]
				else:
					var = str(filedictold[key])
					var1 = str(filedict[key])
					if var != var1:
						updated[key] = filedict[key]
			for key in filedict.keys():
				if (not filedictold.has_key(key)):
					added[key] = filedict[key]
			if added:
				for akey,(actime,amtime) in added.items():
						for dkey in deleted.keys():
							var =  str(actime)
							var1 =  str(deleted[dkey][1:len(str(actime))+1])
							if var[0:-2] == var1[0:-2]:
								renamed[dkey] = akey
								del added[akey]
								del deleted[dkey]		
			if renamed:
				print "renamed"
				print renamed
				for key in renamed.iterkeys():
					key = key.split("Sync-n-Share")
					print key[-1]
					key2 = renamed[key].split("Sync-n-Share")
					clientSync.init("rename", "Sync-n-Share"+key[-1]+' '+"Sync-n-Share"+key2[-1])
			if added: 
				print "added" 
				print added
				for key in added.iterkeys():
					print key
					key = key.split("Sync-n-Share")
					print key[-1]
					clientSync.init("add", "Sync-n-Share"+key[-1])
			if deleted:
				print "deleted"  
				print deleted
				for key in deleted.iterkeys():
					key = key.split("Sync-n-Share")
					print key[-1]
				#	clientSync.init("delete", "Sync-n-Share"+key[-1])
			if updated:
				print "updated" 
				print updated
				for key in updated.iterkeys():
					key = key.split("Sync-n-Share")
					print key[-1]
					clientSync.init("modify", "Sync-n-Share"+key[-1])
			createfilelog(filedict)			
		time.sleep(2)
		filedictold = filedict.copy()
		filedict.clear()
		time.sleep(2)
		gettimelog("Sync-n-Share")
