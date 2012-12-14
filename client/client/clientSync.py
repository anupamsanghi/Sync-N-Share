import socket
import sys
import time

def LCS(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0] * (n+1) for i in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if X[i-1] == Y[j-1]: 
                C[i][j] = C[i-1][j-1] + 1
            else:
                C[i][j] = max(C[i][j-1], C[i-1][j])
    return C

# for finding only 1 lcs	
def backTrack(C, X, Y, i, j):
    if i == 0 or j == 0:
        return ""
    elif X[i-1] == Y[j-1]:
        return backTrack(C, X, Y, i-1, j-1) + X[i-1]
    else:
        if C[i][j-1] > C[i-1][j]:
            return backTrack(C, X, Y, i, j-1)
        else:
            return backTrack(C, X, Y, i-1, j)


#for finding the difference	
diff=[]	
def createDiff(C, X, Y,i,j, arr):
    global diff
    if i > 0 and j > 0 and X[i-1] == Y[j-1]:
        createDiff(C, X, Y, i-1, j-1,arr)
    else:
        if j > 0 and (i == 0 or C[i][j-1] >= C[i-1][j]):
            createDiff(C, X, Y, i, j-1,arr)
            diff.append("+^" + str(i) +"^"+ arr[j-1])
        elif i > 0 and (j == 0 or C[i][j-1] < C[i-1][j]):
            createDiff(C, X, Y, i-1, j,arr)
            diff.append("-^" + str(i) +"\n")

def sync(sock, operation, filename):
	#print filename
	try:
		fp=open("userlog",'r')
		for line in fp:
			userinfo = line
		data = operation+'^'+filename
	except:
		print "file missing"
	try:
	    string = userinfo+'^'+data
	    fp.close()
	    sock.send('5'+string)
	    received = sock.recv(1024)
	except:
		print "Unexpected error:", sys.exec_info()[0]
	if operation ==  "add" or operation =="modify":
		#received = sock.recv(1024)
		hashlist1=received.split()
		fp=open("Sync-n-Share"+filename,'r')
		filelist=[]
		hashlist2=[]
		for line in fp:
			hashlist2.append(str(hash(line)))
			filelist.append(line)
		print hashlist1
		print hashlist2
	#	time.sleep(20)
		C = LCS(hashlist1, hashlist2) 
		createDiff(C, hashlist1, hashlist2,len(hashlist1),len(hashlist2),filelist)
		content=''.join(diff)
		#print "content is:"+content
		del diff[0:len(diff)]
		if content=='' and received!=' ':
			print "there were no updations"
		else:
			#print "content is:"+content+"over"
			try:
				sock.send('6'+userinfo+'^'+filename+'^'+content)
			except:
				print "Unexpected error:", sys.exec_info()[0]
			temp = sock.recv(512)

	#sock.close()

def init(sock, updatelist):
	for key, values in updatelist.iteritems():
		if values:
			#print key + ":" + str( values )
			if key == "rename":
				for value in values:
					temp1 = value[0].split("Sync-n-Share")
					oldfile = temp1[-1]
					temp2 = value[1].split("Sync-n-Share")
					newfile = temp2[-1]
					#print oldfile+'^'+newfile
					sync(sock, key, oldfile+"^"+newfile)
			elif key =="delete":
				string = ''
				for value in values:
					value = value.split("Sync-n-Share")
					string = string + value[-1]+ '^'
				sync(sock, key, string)
			else :
				for value in values:
					value = value.split("Sync-n-Share")
					sync(sock, key, value[-1])
