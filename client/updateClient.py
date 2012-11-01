import os
import detect
import os.path, time
def update(sock):
	content = sock.recv(1024)
	content = content.split('^')
	if content[0]=="add":
		addfile(content)
	elif content[0]=="delete":
		delfile(content[1])
	elif content[0]=="modify":
		modfile(content)
	sock.send("done")

def addfile(content):
	filename = content[1]
	print content
	filecontent = content[2:]
	filecontent='^'.join(filecontent)
	filenames=filename			
	filename = filename.split('/')
	print filename
	dirs="/".join(filename[:-1])
	print dirs
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
	print detail
	detect.modoldlog("add",detail)
	
def delfile(filename):
	print filename
	os.remove(filename)


def modfile(content):
	filelist=[]
	filename = content[1]
	print content
	diff = content[2:]
	diff='^'.join(diff)
	print diff
	fp = open(filename,'r+')
	for line in fp:
		filelist.append(line)
	filelist.insert(0,'')
	updatelist=diff.splitlines()
	print updatelist
	subsplit=[]
	for i in range (0,len(updatelist)):
		subsplit.append(updatelist[i].split('^'))
	print subsplit
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
				print string
				j+=1
			filelist[int(subsplit[i][1])]=filelist[int(subsplit[i][1])]+string
			i=j-1
		i+=1
	print filelist
	finalcontent=''.join(filelist)
	print finalcontent
	fp.seek(0)
	fp.truncate()
	fp.write(finalcontent)
	fp.close()	
	absfile = os.path.abspath(filename)
	detail = str(os.path.getmtime(absfile))+','+str(os.path.getctime(absfile))	
	print detail
	detect.modoldlog("modify",absfile+':'+detail)
