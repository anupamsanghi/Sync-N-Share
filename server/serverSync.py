import socket
import os
import MySQLdb
def sync(repoid, filename):
	filelist=[]
	hashlist=[]
	version=0
	filename = filename.replace('/','^')
	filename = repoid+'^'+filename
	while True:
		version+=1
		try:			
			fp=open(filename+'^'+str(version),'r')
		except:
			version-=1
			break
	if version==0:
		content=' '
	else:
		fp=open(filename+'^'+str(version),'r')
		for line in fp:
			filelist.append(line)
			hashlist.append(str(hash(line)))
		content=' '.join(hashlist)
		fp.close()
	client_socket.send(content)
	diff=""
	while True:
		patch = client_socket.recv(512)
		if not patch:
			break
		diff=diff+patch
	print diff
	if diff!='':
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
				string=subsplit[i][2]+'\n'
				while j<len(subsplit) and subsplit[j][1]==subsplit[j-1][1]:
					string=string+subsplit[j][2]+'\n'
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
if __name__ == "__main__":
	#creating server socketpath_arr = path.split('/')
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("", 5000))	
	while 1:
		server_socket.listen(5)
		print "TCPServer Waiting for client on port 5000"
		client_socket, address = server_socket.accept()
		print "I got a connection from ", address
		print "in"
		data = client_socket.recv(512)
		print data
		user_content = data.split('^')
		user = user_content[0]
		userpc = user_content[1]
		path = user_content[3]
		path1 = path
		operation = user_content[2]
		filelist=[]
		hashlist=[]
		path_arr = path.split('/')
		if len(path_arr)>1:
			repository = path_arr[0]
			filename = "/".join(path_arr[1:])
		else:
			repository=None
			filename=path_arr[0]
		print repository
		print filename
		db = MySQLdb.connect( user="root", unix_socket="/opt/lampp/var/mysql/mysql.sock",passwd="", host="localhost",db="os_minor")
		cur = db.cursor() 
		cur.execute("SELECT * FROM members, project_info WHERE members.username ='"+ user+"' and project_info.projectname = '"+repository+"' and project_info.projectid = members.projectid")
		resultset = cur.fetchall()
		if operation=="add":
			if len(resultset) == 0:
				cur.execute("select * from project_info")
				result=cur.fetchall()
				repoid=str(len(result)+1)
				cur.execute("INSERT INTO project_info VALUES('"+repoid+"', '"+repository+"', 0)")
				cur.execute("INSERT INTO members VALUES('"+user+"', '"+repoid+"')")
				cur.execute("INSERT INTO files(projectid,filename,modified_by,versions) VALUES('"+repoid+"', '"+filename+"', '"+user+"', '1' )")
				cur.execute("SELECT username FROM members WHERE projectid='"+repoid+"'")
				res = cur.fetchall()
				for row in res:
					if row[0]!=user:
						cur.execute("INSERT INTO updations VALUES('"+repoid+'^'+filename+"', 'add', '"+row[0]+"')")
				cur.close()
				db.commit()
			else:
				repoid = resultset[0][1]
				cur.execute("INSERT INTO files(projectid,filename,modified_by,versions) VALUES('"+repoid+"', '"+filename+"', '"+user+"', '1' )")
				cur.close()
				db.commit()
			content=' '
			sync(repoid,filename)
			print "added" + filename
		elif operation == "delete":
			repoid = resultset[0][1]
			sql = "UPDATE project_info SET hide = %s WHERE projectid = %s" 
			params = (1, repoid)
			cur.execute(sql, params)
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
			#change filename at server filesystem
		
		elif operation == "modify":
			repoid = resultset[0][1]
			cur.execute("UPDATE files SET modified_by = '"+user+"', versions = versions + 1 WHERE projectid = '"+repoid+"' AND filename = '"+filename+"'")
			cur.close()
			db.commit()
			#print filename
			#fp=open(filename,'r')
			#for line in fp:
			#	filelist.append(line)
			#	hashlist.append(str(hash(line)))
			#content=' '.join(hashlist)
			#fp.close()
			sync(repoid,filename)
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
