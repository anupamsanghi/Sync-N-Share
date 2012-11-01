def getInfo():
	fp = open("userlog",'r')
	for line in fp:
		userinfo = line
	return userinfo

def createUserlog(userinfo):
	fp = open('userlog','w')
	userinfo = userinfo.split(',')
	fp.write(userinfo[0]+'^'+userinfo[2])
