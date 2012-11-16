def getUpdates(data1, db,clientsock):
	cur = db.cursor() 
	string = ''
	cur.execute("SELECT * FROM updations WHERE username ='"+ data1+"'")
	resultset = cur.fetchall()
	count = len(resultset)
	#print count
	clientsock.send(str(count))
	op = clientsock.recv(1024)
	if op=='1':
		if count!=0:
			for row in resultset:
				string = ''
				if row[1] == "add":
					filename=row[0].replace("/",'^')
					filename1 = row[0].split('^')
					cur.execute("SELECT versions FROM files WHERE projectid = '"+filename1[0]+"' AND filename ='"+filename1[1]+"'")
					res = cur.fetchall()
					version = res[0][0] 
					filename = filename+'^'+str(version)
					fp = open(filename,'r')
					for line in fp:
						string = string +line
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename1[0]+"'")
					res = cur.fetchall()
					content = "add"+'^'+"Sync-n-Share/"+res[0][0]+'/'+filename1[1]+'^'+string
					#print content
				elif row[1] == "delete":
					filename = row[0].split('^')
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename[0]+"'")
					res = cur.fetchall()
					content = "delete"+'^'+"Sync-n-Share/"+res[0][0]+'/'+filename[1]
				elif row[1] == "rename":
					filename = row[0].split('^')
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename[0]+"'")
					res = cur.fetchall()
					filename2 = row[4].split('^')
					content = 'rename^'+'Sync-n-Share/'+res[0][0]+'/'+filename2[1]+'^'+'Sync-n-Share/'+res[0][0]+'/'+filename[1]
				elif row[1] == "modify":
					filename=row[0].replace("/",'^')
					filename1 = row[0].split('^')
					cur.execute("SELECT versions FROM files WHERE projectid = '"+filename1[0]+"' AND filename ='"+filename1[1]+"'")
					res = cur.fetchall()
					version = res[0][0] 
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename1[0]+"'")
					rest = cur.fetchall()
					fp = open(filename+"^"+str((version-1)),'r')
					for line in fp:
						string = string +line
					#print string
					content = "modify"+'^'+"Sync-n-Share/"+rest[0][0]+"/"+filename1[1]+"^"+string
				clientsock.send(content)
				data = clientsock.recv(1024)
				if not data =="done":
					#print data
					filename=row[0].replace("/",'^')
					filename1 = row[0].split('^')
					cur.execute("SELECT versions FROM files WHERE projectid = '"+filename1[0]+"' AND filename ='"+filename1[1]+"'")
					res = cur.fetchall()
					version = res[0][0] 
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename1[0]+"'")
					rest = cur.fetchall()
					fp = open(filename+"^"+str((version)),'r')
					string = ''
					for line in fp:
						string = string +line
					clientsock.send(string)
				cur.execute("DELETE FROM updations WHERE operation_id='"+str(row[3])+"'")
#	db.commit()
