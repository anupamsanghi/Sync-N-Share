import socket
import os
import MySQLdb
def rename(fileold, filenew, repoid):
	for filename in os.listdir("."):
		if filename.startswith(repoid+'^'+fileold+'^'):
			version = filename[-1]
			os.rename(filename, repoid+'^'+filenew+'^'+version)
def sync(repoid, filename, sock):
	filelist=[]
	hashlist=[]
	version=0
	filename = filename.replace('/','^')
	filename = repoid+'^'+filename
	#print filename
	while True:
		version+=1
		try:			
			fp=open(filename+'^'+str(version),'r')
			fp.close()
		except:
			version-=1
			break
	#print version
	if version==0:
		content=' '
	else:
		fp=open(filename+'^'+str(version),'r')
		for line in fp:
			filelist.append(line)
			hashlist.append(str(hash(line)))
		content=' '.join(hashlist)
		fp.close()
	#print "content is:"+content
	sock.send(content)
	diff = sock.recv(512)
	filelist.insert(0,'')
	updatelist=diff.splitlines()
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
				#print string
				j+=1
			filelist[int(subsplit[i][1])]=filelist[int(subsplit[i][1])]+string
			i=j-1
		i+=1
	#print filelist
	finalcontent=''.join(filelist)
	#print finalcontent
	fp=open(filename+'^'+str(version+1),'w')
	fp.write(finalcontent)
	fp.close()
	if version>0:
		fp=open(filename+'^'+str(version),'w')
		fp.write(diff)
		fp.close()
	
def update(db,sock):
	data = sock.recv(512)
	#print data
	user_content = data.split('^')
	user = user_content[0]
	userpc = user_content[1]
	operation = user_content[2]
	if operation != "delete":	
		path = user_content[3]
		path_arr = path[1:].split('/')
		if len(path_arr)>1:
			repository = path_arr[0]
			filename = "/".join(path_arr[1:])
		else:
			repository=' '
			filename=path_arr[0]
		#print repository
		#print filename
		cur = db.cursor() 
		cur.execute("SELECT * FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository+"' and project_info.projectid = members.projectid")
		resultset = cur.fetchall()
	if operation=="add":
		filelist=[]
		hashlist=[]
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
				sql = "UPDATE files SET modified_by = '"+user+"', versions = versions+1, hide = %s WHERE projectid = %s AND filename  = %s" 
				params = (0, repoid, filename)
				cur.execute(sql, params)
		content=' '		
		sync(repoid,filename, sock)
		cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
		res = cur.fetchall()
		for row in res:
			if row[0]!=user:
				cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'add', '"+row[0]+"')")	
		cur.close()
		db.commit()
		#print "added" + filename
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
			#print repository
			#print filename
			cur = db.cursor() 
			cur.execute("SELECT * FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository+"' and project_info.projectid = members.projectid")
			resultset = cur.fetchall()
			repoid = resultset[0][1]
			sql = "UPDATE files SET modified_by = '"+user+"', hide = %s WHERE projectid = %s AND filename  = %s" 
			params = (1, repoid, filename)
			cur.execute(sql, params)
			db.commit()
			cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
			res = cur.fetchall()
			for row in res:
				if row[0]!=user:
					cur.execute("SELECT operation,operation_id,filename_old FROM updations WHERE username='"+row[0]+"' AND filename ='"+repoid+'^'+filename+"'")
					filevalues = cur.fetchall()
					if len(filevalues) == 0:
						cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'delete', '"+row[0]+"')")
					elif filevalues[0][0] == "add":
						cur.execute("DELETE FROM updations WHERE operation_id = '"+str(filevalues[0][1])+"'")
					elif filevalues[0][0] == "modify":
						cur.execute("UPDATE updations SET operation = 'delete', filename = '"+repoid+'^'+filename+"', filename_old = '' WHERE operation_id = '" +str(filevalues[0][1])+"'")		
					else:
						cur.execute("UPDATE updations SET operation = 'delete', filename = '"+filevalues[0][2]+"', filename_old = '' WHERE operation_id = '" +str(filevalues[0][1])+"'")			
			cur.close()
			db.commit()
			#print "deleted " + filename
	elif operation == "rename":
		path1 = user_content[3]
		path2 = user_content[4]
		repoid = resultset[0][1]
		path2 = path2.split('/')
		filename2 = path2[-1]
		cur.execute("UPDATE files SET filename = '"+filename2+"', modified_by = '"+user+"' WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")
		db.commit()
		rename(filename, filename2, repoid)
		cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
		res = cur.fetchall()
		for row in res:
			if row[0]!=user:
				cur.execute("SELECT operation,operation_id FROM updations WHERE username='"+row[0]+"' AND filename ='"+repoid+'^'+filename+"'")
				filevalues = cur.fetchall()
				if len(filevalues) == 0 :
					cur.execute("INSERT INTO updations(filename,operation,username,filename_old) VALUES('"+repoid+'^'+filename2+"', 'rename', '"+row[0]+"', '"+repoid+'^'+filename+"')")
				else:
					if filevalues[0][0] == "add":
						cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename2+"', 'add', '"+row[0]+"')")
						cur.execute("DELETE FROM updations WHERE operation_id = '"+str(filevalues[0][1])+"'")
					elif filevalues[0][0] == "modify":
						cur.execute("DELETE FROM updations WHERE operation_id = '"+str(filevalues[0][1])+"'")
						cur.execute("INSERT INTO updations(filename,operation,username, filename_old) VALUES('"+repoid+'^'+filename2+"', 'rename', '"+row[0]+"', '"+repoid+'^'+filename+"')")
	#					cur.execute("UPDATE updations SET filename = '"+filename2+"' WHERE operation_id = '"+str(filevalues[0][1])+"'")						
						cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename2+"', 'modify', '"+row[0]+"')")
				
					else:
						cur.execute("UPDATE updations SET filename = '"+repoid+'^'+filename2+"' WHERE operation_id = '"+str(filevalues[0][1])+"'")
						#cur.execute("DELETE FROM updations WHERE operation_id ='"+str(filevalues[0][1])+"'")
		cur.close()
		db.commit()	
	elif operation == "modify":
		filelist=[]
		hashlist=[]
		repoid = resultset[0][1]
		cur.execute("UPDATE files SET modified_by = '"+user+"', versions = versions + 1 WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")	
		cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
		res = cur.fetchall()		
		sync(repoid,filename, sock)
		for row in res:
			if row[0]!=user:
				cur.execute("SELECT operation,operation_id, filename_old FROM updations WHERE username='"+row[0]+"' AND filename ='"+repoid+'^'+filename+"'")
				filevalues = cur.fetchall()
				if len(filevalues) == 0:
					cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'modify', '"+row[0]+"')")
				else:
					if filevalues[0][0] == "add":
						cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'add', '"+row[0]+"')")
						cur.execute("DELETE FROM updations WHERE operation_id = '"+str(filevalues[0][1])+"'")
					elif filevalues[0][0] == "modify":
						cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'modify', '"+row[0]+"')")
						cur.execute("DELETE FROM updations WHERE operation_id = '"+str(filevalues[0][1])+"'")
				
					else:
												
						cur.execute("INSERT INTO updations(filename,operation,username) VALUES('"+repoid+'^'+filename+"', 'modify', '"+row[0]+"')")			
						
				#		cur.execute("DELETE FROM updations WHERE operation_id = '"+str(filevalues[0][1])+"'")
					#	cur.execute("INSERT INTO updations(filename,operation,username,filename_old) VALUES('"+repoid+'^'+filename+"','rename', '"+row[0]+"', '"+filevalues[0][2]+"')")
		cur.close()
		db.commit()
		##print filename
		#fp=open(filename,'r')
		#for line in fp:
		#	filelist.append(line)
		#	hashlist.append(str(hash(line)))
		#content=' '.join(hashlist)
		#fp.close()
		#print "modified" + filename
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
