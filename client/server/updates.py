import connectFilesystem

def getdiff(virtualfile):
	print "in getdiff"
	diff = []	
	linenumber = 0
	for line in virtualfile:
		print "in for loop"
		print line[0]
		if line[0] != '#':
			print "in whileloop"
			diff.append('+^'+str(linenumber)+'^'+line)
			print diff
		#print "out1"
		else:
			for i in range(linenumber+1, int(line[1])):
				print "in forloop2"
				diff.append('-^'+str(i))
			print "out"
			print line
			linenumber = int(line[1:])
	return ''.join(diff)

def getfinalfile(virtualfile, diff, filename):
	print "in getfinalfile"
	virtualfile.insert(0,'')
	#fp = open("../filesystem/"+filename+'^'+str(diff), 'r')
	#string = ''
	#for line in fp:
	#	string = string +line
	sock = connectFilesystem.createCon()
	string = connectFilesystem.getResponse("1"+filename+'^'+str(diff),sock)
	connectFilesystem.closeCon(sock)
	updatelist=string.splitlines()
	print updatelist
	subsplit=[]
	for i in range (0,len(updatelist)):
		subsplit.append(updatelist[i].split('^'))
	i=0
	while i<len(subsplit):
		if subsplit[i][0]=='-':
			virtualfile[int(subsplit[i][1])]=''
		elif subsplit[i][0]=='+':
			j=i+1
			string = '^'.join(subsplit[i][2:])
			string = string + '\n'
			while j<len(subsplit) and subsplit[j][1]==subsplit[j-1][1]:
				string1='^'.join(subsplit[j][2:])
				string = string + string1 +'\n'
				j+=1
			virtualfile[int(subsplit[i][1])]=virtualfile[int(subsplit[i][1])]+string
			i=j-1
		i+=1	
	virtualfile = "".join(virtualfile)
	virtualfile = virtualfile.splitlines()
	for i in range (0,len(virtualfile)-1):
		virtualfile[i] = virtualfile[i]+"\n"
	print virtualfile
	return virtualfile

def createVirtualFile(filename):
	sock = connectFilesystem.createCon()
	string = connectFilesystem.getResponse("1"+filename,sock)
	connectFilesystem.closeCon(sock)
	
#	fp = open("../filesystem/"+filename, 'r')
#	string = ''
#	for line in fp:
#		string = string +line
	updatelist=string.splitlines()
	print updatelist
	temp = updatelist[-1].split('^')
	linecount = temp[1]
	print linecount	
	virtualfile =[]
	for i in range (0,int(linecount)):
		virtualfile.append("#"+str(i+1)+"\n")	
	#virtualfile.insert(0,'')
	virtualfile.append(str(int(linecount)+1)+'#')
	print virtualfile	
	return virtualfile



def init(request, db):
	username = (request.split('^'))[0]
	cur = db.cursor() 
	cur.execute("SELECT * FROM updations WHERE username ='"+username+"'")
	return cur.fetchall()


def getCount(request, db):
	return str(len(init(request, db)))


def getUpdate(request, db):
	string = ''
	cur = db.cursor() 
	resultset = init(request, db)
	if resultset[0][1] == "add":
		filename=resultset[0][0].replace("/",'^')
		filename1 = resultset[0][0].split('^')
		cur.execute("SELECT versions FROM files WHERE projectid = '"+filename1[0]+"' AND filename ='"+filename1[1]+"'")
		res = cur.fetchall()
		version = res[0][0] 
		filename = filename+'^'+str(version)
		sock = connectFilesystem.createCon()
		string = connectFilesystem.getResponse("1"+filename,sock)
		connectFilesystem.closeCon(sock)
	
#		fp = open("../filesystem/"+filename,'r')
#		for line in fp:
#			string = string +line
		cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename1[0]+"'")
		res = cur.fetchall()
		content = "add"+'^'+"Sync-n-Share/"+res[0][0]+'/'+filename1[1]+'^'+string
	elif resultset[0][1] == "delete":
		filename = resultset[0][0].split('^')
		cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename[0]+"'")
		res = cur.fetchall()
		content = "delete"+'^'+"Sync-n-Share/"+res[0][0]+'/'+filename[1]
	elif resultset[0][1] == "rename":
		filename = resultset[0][0].split('^')
		cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename[0]+"'")
		res = cur.fetchall()
		filename2 = resultset[0][4].split('^')
		content = 'rename^'+'Sync-n-Share/'+res[0][0]+'/'+filename2[1]+'^'+'Sync-n-Share/'+res[0][0]+'/'+filename[1]
	elif resultset[0][1] == "modify":
		print "in modify"
		filename=resultset[0][0].replace("/",'^')
		filename1 = resultset[0][0].split('^')
		cur.execute("SELECT versions FROM files WHERE projectid = '"+filename1[0]+"' AND filename ='"+filename1[1]+"'")
		res = cur.fetchall()
		version = int(res[0][0]) 
		print version
		cur.execute("SELECT version FROM updations WHERE operation = 'modify' AND filename ='"+filename1[0]+'^'+filename1[1]+"'")
		res = cur.fetchall()
		version2 = int(res[0][0])
		version2 -=1
		cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename1[0]+"'")
		rest = cur.fetchall()
		print version
		print version2
		if version>version2+1:
			virtualfile = createVirtualFile(filename1[0]+'^'+filename1[1]+'^'+str(version2))
			for i in range (version2, version):
				virtualfile = getfinalfile(virtualfile, i, filename1[0]+'^'+filename1[1])
			string = getdiff(virtualfile)
		else:
			sock = connectFilesystem.createCon()
			string = connectFilesystem.getResponse("1"+filename+'^'+str(version-1),sock)
			connectFilesystem.closeCon(sock)
	
	#		fp = open("../filesystem/"+filename+"^"+str((version-1)),'r')
	#		for line in fp:
	#			string = string +line
			print string
		content = "modify"+'^'+"Sync-n-Share/"+rest[0][0]+"/"+filename1[1]+"^"+string
	cur.execute("DELETE FROM updations WHERE operation_id='"+str(resultset[0][3])+"'")
	db.commit()
	return content

def getFileContent(request, db):
	cur = db.cursor()
	request = request.split('^')
	user = request[0]
	filepath = ''.join(request[1:])
	filepath = filepath.split('/')
	repository = filepath[1]
	filename = ('^').join(filepath[2:])
	print user
	print repository
	cur.execute("SELECT project_info.projectid FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository+"' and project_info.projectid = members.projectid")
	result = cur.fetchall()
	print result[0][0]
	print filename
	cur.execute("SELECT versions FROM files WHERE projectid = '"+result[0][0]+"' AND filename ='"+filename+"'")
	res = cur.fetchall()
	version = res[0][0]
	sock = connectFilesystem.createCon()
	string = connectFilesystem.getResponse("1"+result[0][0]+'^'+filename+"^"+str(version),sock)
	connectFilesystem.closeCon(sock)
	
	#fp = open("../filesystem/"+result[0][0]+'^'+filename+"^"+str(version),'r')
	#string = ''
	#for line in fp:
	#	string = string +line
	return string
