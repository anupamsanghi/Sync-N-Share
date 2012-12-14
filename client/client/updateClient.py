import os
import detect
import os.path, time
import filecmp
import shutil
import connectify
import copy
import userlog

def checkConcurrency(content, updatelist, sock):
	temp = copy.deepcopy(updatelist)
	if len(updatelist["add"]) == 0 and len(updatelist["delete"]) ==0 and len(updatelist["modify"]) == 0 and len(updatelist["rename"]) == 0:
		#print "in outerelse"
		update(content)
		#sock.send("done")
	else:
		#print updatelist
		userinfo = userlog.getInfo()
		username = (userinfo.split('^'))[0]
		for key,values in updatelist.items():
			#print key
			#print values
			filename = []
			for value in values:
				#print key
				if key == "rename":
					print "in rename"
					filename = value[0].split("Sync-n-Share")
					newfile = value[1].split("Sync-n-Share")
					newfile = "Sync-n-Share"+newfile[-1]
				else:
					filename = value.split("Sync-n-Share")
				filename = "Sync-n-Share"+filename[-1]
			#	print content[1]
			#	print filename
				flag = content[1] == filename
				print flag
				if flag:
					if content[0] == "add":
			#			print "in add"
						string = ''
						fp = open(filename, 'r')
						for line in fp:
							string = string + line
						fp.close()
						match = string == content[2]
						if match:
							temp["add"].remove(value)
						else:
							temp["add"].remove(value)
							temp["add"].append(value+"Conflicted_Copy")
							renamefile(filename, filename+"Conflicted_Copy")
							addfile(content)
		#				sock.send("done")	
					elif content[0] == "delete":
						if key == "modify":
							temp["add"].append(value)
							temp["modify"].remove(value)
						elif key == "delete":
							temp["delete"].remove(value)
						else :
			#				print "delete - rename section"
							temp["add"].append(newfile)
							temp["rename"].remove(value)
		#				sock.send("done")	
					elif content[0] == "modify":
						if key == "modify":
							filecontent = connectify.getResponse('4'+username+'^'+content[1],sock)
						#	print filecontent
							string = ''
							fp = open(filename, 'r')
							for line in fp:
								string = string + line
							fp.close()
							match = string == filecontent
							if not match:
								temp["add"].append(value+"Conflicted_Copy")
								renamefile(filename, filename+"Conflicted_Copy")
								content[2] = filecontent
								del content[3:]
							#	print content
								addfile(content)
							temp["modify"].remove(value)
						elif key == "delete":
							filecontent = connectify.getResponse('4'+username+'^'+content[1],sock)
							content[2] = filecontent
							del content[3:]
							addfile(content)
							temp["delete"].remove(value)
						else :
							string = ''
							fp = open(newfile, 'r')
							for line in fp:
								string = string + line
							fp.close()
							content2 = ["add",filename,string]
							addfile(content2)
							temp["add"].append(value[1])
							temp["rename"].remove(value)
							modfile(content)
		#					sock.send("done")	
					elif content[0]== "rename":
						if key == "modify":
							filecontent = connectify.getResponse('4'+username+'^'+content[1],sock)
							content[1] = content[2]
							content[2] = filecontent
							addfile(content)
							temp["add"].append(value)
							temp["modify"].remove(value)	
						elif key == "delete":
							filecontent = connectify.getResponse('4'+username+'^'+content[1],sock)
							content[1] = content[2]
							content[2] = filecontent
							addfile(content)
							temp["delete"].remove(value)
						else :
							if not content[2] == newfile:
								string = ''
								fp = open(newfile, 'r')
								for line in fp:
									string = string + line
								fp.close()
								content2 = "add^"+content[2]+'^'+string
								temp["add"].append(value[1])
								print "rename content2 is"+content2
								content2 = content2.split('^')
								addfile(content2)
							temp["rename"].remove(value)
		#					sock.send("done")
				else:
					#print "in else"
					update(content)
		#			sock.send("done")	
	updatelist = temp		
	print "latest updatelist :" 
	print  updatelist
	return updatelist
	#print "temp is :"

def update(content):
	if content[0]=="add" :
		addfile(content)
	elif content[0]=="delete":
		delfile(content[1])
	elif content[0]=="modify":
		modfile(content)
	elif content[0] == "rename":
		renamefile(content[1],content[2])

def init(sock, updatelist):
	content = sock.recv(1024)
	content = content.split('^')
	updatelist = checkConcurrency(content, updatelist, sock)
	return updatelist

def addfile(content):
	filename = content[1]
	print content
	filecontent = content[2:]
	filecontent='^'.join(filecontent)
	filenames=filename			
	filename = filename.split('/')
	#print filename
	dirs="/".join(filename[:-1])
	#print dirs
	if dirs!="":	
		if not os.path.exists(dirs):
			os.makedirs(dirs)
	if os.path.exists(filenames):
		fp = open(filenames,'r+')
	else:
		fp = open(filenames,'w')
	fp.write(filecontent)
	fp.close()	
	absfile = os.path.abspath(filenames)
	detail = {absfile:str(os.path.getmtime(absfile))+','+str(os.path.getctime(absfile))}	
	#print detail
	detect.modoldlog("add",detail)
	
def delfile(filename):
	#print filename
	absfile = os.path.abspath(filename)
	detail = {absfile:str(os.path.getmtime(absfile))+','+str(os.path.getctime(absfile))}	
	os.remove(filename)
	detect.modoldlog("delete",absfile)

def modfile(content):
	filelist=[]
	filename = content[1]
	#print content
	diff = content[2:]
	diff='^'.join(diff)
	#print diff
	fp = open(filename,'r+')
	for line in fp:
		filelist.append(line)
	filelist.insert(0,'')
	updatelist=diff.splitlines()
	#print updatelist
	subsplit=[]
	for i in range (0,len(updatelist)):
		subsplit.append(updatelist[i].split('^'))
	#print subsplit
	i=0
	while i<len(subsplit):
		if subsplit[i][0]=='-':
			filelist[int(subsplit[i][1])]=''
		elif subsplit[i][0]=='+':
			j=i+1
			string = '^'.join(subsplit[i][2:])
			string = string + '\n'
			while j<len(subsplit) and subsplit[j][1]==subsplit[j-1][1]:
				string1='^'.join(subsplit[j][2:])
				string = string + string1 +'\n'
	#			print string
				j+=1
			filelist[int(subsplit[i][1])]=filelist[int(subsplit[i][1])]+string
			i=j-1
		i+=1
	#print filelist
	finalcontent=''.join(filelist)
	#print finalcontent
	fp.seek(0)
	fp.truncate()
	fp.write(finalcontent)
	fp.close()	
	absfile = os.path.abspath(filename)
	detail = str(os.path.getmtime(absfile))+','+str(os.path.getctime(absfile))	
	#print detail
	detect.modoldlog("modify",absfile+':'+detail)

def renamefile(oldfile,newfile):
	absfile1 = os.path.abspath(oldfile)
	absfile2 = os.path.abspath(newfile)
	#print oldfile
	#print newfile
	os.rename(oldfile, newfile)
	detail = {absfile2:str(os.path.getmtime(absfile2))+','+str(os.path.getctime(absfile2))}	
	#print str(detail)
	detect.modoldlog("rename",absfile1+'^'+str(detail))
