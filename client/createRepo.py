import os
import errno
if __name__=="__main__":
	try:
		os.mkdir('Sync-n-Share')
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise
