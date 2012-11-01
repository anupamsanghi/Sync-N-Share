import socket
import os
import MySQLdb
def sync(repoid, filename, sock):
	filelist=[]
	hashlist=[]
	version=0
	filename = filename.replace('/','^')
	filename = repoid+'^'+filename
	print filename
	while True:
		version+=1
		try:			
			fp=open(filename+'^'+str(version),'r')
			fp.close()
		except:
			version-=1
			break
	print version
	if version==0:
		content=' '
	else:
		fp=open(filename+'^'+str(version),'r')
		for line in fp:
			filelist.append(line)
			hashlist.append(str(hash(line)))
		content=' '.join(hashlist)
		fp.close()
	print "content is:"+content
	sock.send(content)
	print "finding diff"
	#diff=""
	diff = sock.recv(512)
	print diff
#	if diff!='':
	filelist.insert(0,'')
		#filelist.append('')
	updatelist=diff.splitlines()
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
	fp=open(filename+'^'+str(version+1),'w')
	fp.write(finalcontent)
	fp.close()
	if version>0:
		fp=open(filename+'^'+str(version),'w')
		fp.write(diff)
		fp.close()
	
def update(db,sock):
	data = sock.recv(512)
	print data
	user_content = data.split('^')
	user = user_content[0]
	userpc = user_content[1]
	operation = user_content[2]
	if operation != "delete":
		filelist=[]
		hashlist=[]	
		path = user_content[3]
		path_arr = path[1:].split('/')
		if len(path_arr)>1:
			repository = path_arr[0]
			filename = "/".join(path_arr[1:])
		else:
			repository=' '
			filename=path_arr[0]
		print repository
		print filename
		cur = db.cursor() 
		cur.execute("SELECT * FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository+"' and project_info.projectid = members.projectid")
		resultset = cur.fetchall()
	if operation=="add":
		if len(resultset) == 0:
			cur.execute("select * from project_info")
			result=cur.fetchall()
			repoid=str(len(result)+1)
			cur.execute("INSERT INTO project_info VALUES('"+repoid+"', '"+repository+"')")
			cur.execute("INSERT INTO members VALUES('"+user+"', '"+repoid+"')")
			cur.execute("INSERT INTO files(projectid,filename,modified_by,versions) VALUES('"+repoid+"', '"+filename+"', '"+user+"', '1' )")
		else:
			repoid = resultset[0][1]
			cur.execute("SELECT * FROM files WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")
			rest = cur.fetchall()
			if len(rest)== 0:
				cur.execute("INSERT INTO files(projectid,filename,modified_by,versions) VALUES('"+repoid+"', '"+filename+"', '"+user+"', '1' )")
			else:
				sql = "UPDATE files SET modified_by = '"+user+"', hide = %s WHERE projectid = %s AND filename  = %s" 
				params = (0, repoid, filename)
				cur.execute(sql, params)
		content=' '		
		sync(repoid,filename, sock)
		cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
		res = cur.fetchall()
		for row in res:
			if row[0]!=user:
				cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"^1', 'add', '"+row[0]+"')")	
		cur.close()
		db.commit()
		print "added" + filename
	elif operation == "delete":
		for i in range (3, len(user_content)):
			path = user_content[i]
			path_arr = path[1:].split('/')
			if len(path_arr)>1:
				repository = path_arr[0]
				filename = "/".join(path_arr[1:])
			else:
				repository=' '
				filename=path_arr[0]
			print repository
			print filename
			cur = db.cursor() 
			cur.execute("SELECT * FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository+"' and project_info.projectid = members.projectid")
			resultset = cur.fetchall()
			repoid = resultset[0][1]
			sql = "UPDATE files SET modified_by = '"+user+"', hide = %s WHERE projectid = %s AND filename  = %s" 
			params = (1, repoid, filename)
			cur.execute(sql, params)
			cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
			res = cur.fetchall()
			for row in res:
				if row[0]!=user:
					cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'delete', '"+row[0]+"')")
			cur.close()
			db.commit()
			print "deleted " + filename
	elif operation == "rename":
		path2 = user_content[4]
		path_arr2 = path2.split('/')
		if len(path_arr2)>1:
			filename2 = "/".join(path_arr2[1:])
		else:
			filename2=path_arr2[0]
		repoid = resultset[0][1]
		cur.execute("UPDATE files SET filename = '"+filename2+"', modified_by = '"+user+"', WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")
		cur.close()
		db.commit()	
	elif operation == "modify":
		repoid = resultset[0][1]
		cur.execute("UPDATE files SET modified_by = '"+user+"', versions = versions + 1 WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")	
		cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
		res = cur.fetchall()		
		sync(repoid,filename, sock)
		for row in res:
			if row[0]!=user:
				cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'modify', '"+row[0]+"')")
		cur.close()
		db.commit()
		#print filename
		#fp=open(filename,'r')
		#for line in fp:
		#	filelist.append(line)
		#	hashlist.append(str(hash(line)))
		#content=' '.join(hashlist)
		#fp.close()
		print "modified" + filename
	elif operation=="move":
		path2 = user_content[4]
		path_arr2 = path2.split('/')
		if len(path_arr2)>1:
			repository2 = path_arr2[0]
			filename2 = "/".join(path_arr2[1:])
		else:
			repository2=None
			filename2=path_arr2[0]
			repoid = resultset[0][1]
			filename = filename.replace('/','^')
			filename = repoid+'^'+filename
			filename2 = filename2.replace('/','^')
		if repository == repository2:
			cur.execute("UPDATE files SET filename = '"+filename2+"', modified_by = '"+user+"', WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")
		else:			
			cur.execute("SELECT * FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository2+"' and project_info.projectid = members.projectid")
			resultset2 = cur.fetchall()
			repoid2 = resultset2[0][1]
			cur.execute("UPDATE files SET projectid = '"+repoid2+"', modified_by = '"+user+"', WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")
			filename2 = repoid2+'^'+filename
		for filenames in os.listdir("."):
 			if filenames.startswith(filename):
    				os.rename(filenames, filename2+filenames[len(filename):])
		cur.close()
		db.commit()	
	else:
		print "undefined operation" 
