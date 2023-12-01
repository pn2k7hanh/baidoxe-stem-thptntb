from collections import namedtuple
from define import *


kpad=[
	['1','2','3'],
	['4','5','6'],
	['7','8','9'],
	['*','0','#']
]
NO_KEY=0b1111


def decode(a):
	data=dict()
	tp=a>>5 # get 3 last bit for type
	if tp==0b000: # ir sensor signal
		data['type']='irsensor'
		for i in range(4):
			if getbit(a,i)==1:
				data['irsensor'+str(i+1)]='check-square-o'
			else:
				data['irsensor'+str(i+1)]='square-o'
		if getbit(a,4)==1:
			data['state']='check-square-o'
		else:
			data['state']='square-o'
	elif tp==0b001: # flame sensor signal
		data['type']='flamesensor'
		# val=a%(2**5)
		# data['value']=val
		data['value']=getbit(a,0)
	elif tp==0b011: # keypad signal
		data['type']='keypad'
		val=a%(2**4)
		if val==NO_KEY:
			data['key']='n'
		else:
			data['key']=kpad[val>>2][val%(2**2)]
	else:
		data['type']='unknowed'
	return data