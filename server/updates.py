def getUpdates(data1, db,clientsock):
	cur = db.cursor() 
	string = ''
	cur.execute("SELECT * FROM updations WHERE username ='"+ data1+"'")
#	db.commit()
	resultset = cur.fetchall()
	count = len(resultset)
	print count
	clientsock.send(str(count))
	op = clientsock.recv(1024)
	print "hi"
	if op=='1':
		if count!=0:
			for row in resultset:
				if row[1] == "add":
					filename=row[0].replace("/",'^')
					print filename
					fp = open(filename,'r')
					for line in fp:
						string = string +line			
					filename=row[0].split('^')
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename[0]+"'")
					res = cur.fetchall()
					content = "add"+'^'+"Sync-n-Share/"+res[0][0]+'/'+filename[1]+'^'+string
					print content
				elif row[1] == "delete":
					filename = row[0].split('^')
					cur.execute("SELECT projectname FROM project_info WHERE projectid = '"+filename[0]+"'")
					res = cur.fetchall()
					content = "delete"+'^'+"Sync-n-Share/"+res[0][0]+'/'+filename[1]
				elif row[1] == "rename":
					print "rename"
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
					print string
					content = "modify"+'^'+"Sync-n-Share/"+rest[0][0]+"/"+filename1[1]+"^"+string
				clientsock.send(content)
				data = clientsock.recv(1024)
				if data =="done":
					cur.execute("DELETE FROM updations WHERE operation_id='"+str(row[3])+"'")
#	db.commit()
