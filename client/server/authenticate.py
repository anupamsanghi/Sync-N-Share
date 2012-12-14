def auth(data, db):
	cur = db.cursor() 
	userinfo = data.split(',')
	cur.execute("SELECT * FROM user_info WHERE username = '"+userinfo[0]+"' and password = '"+userinfo[1]+"'")
	resultset = cur.fetchall()
	return str(len(resultset))
