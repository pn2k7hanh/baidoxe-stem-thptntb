def getbit(a,n):
	return (1 if (a&(1<<n)) else 0)

def setbit(a,n,v):
	return (a|(1<<n)) if v else (a&(~(1<<n)))