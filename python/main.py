from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import *

import serialcode as sc
import sys


from define import *
from typingwidget import TypingWidget
from adafruit import Adafruit

class Application(QApplication):
	
	def __init__(self,port,baudrate,argv):
		QApplication.__init__(self,argv)
		self.__define()
		self.defaultPort=port
		self.ard.setPort(QSerialPortInfo(port))
		self.ard.setBaudRate(baudrate)
		
		qDebug('Getting data from Adafruit...')
		self.ada.start()
		while self.ada.first_run:
			pass
		self.ada.runnin=False
		qDebug('Finished!')
		
		# qDebug('Try to connect to arduino...')
		# if self.ard.open(QIODevice.ReadWrite):
		# 	self.typingwidget.show()
		# 	qDebug('Finished!')
		# else:
		# 	qDebug('Failed to open '+port+'!')
		# 	qDebug('Error: '+self.ard.errorString())
		# 	self.ada.runnin=False
		# 	# self.exit(0)
		
		# self.parkingslot=[1]*4
		for i in range(4):
			self.typingwidget.updateParkingSlot(i,False)
		
		self.ard.readyRead.connect(self.__receive_data_arduino)
		self.ada.data_changed.connect(self.__receive_data_adafruit)
		self.typingwidget.getcar.connect(self.__getcar)
		self.typingwidget.parkcar.connect(self.__parkcar)
	def __define(self):
		self.ard=QSerialPort()
		self.ada=Adafruit()
		self.typingwidget=TypingWidget()
		self.ardtimerid=self.startTimer(2000,Qt.VeryCoarseTimer)
		self.defaultPort=''
		self.servotimerid=[-1]*4
		self.parkingslotid=[False]*4
		# None is no event
		# True is getting car
		# False is parking car
		self.parkingslotstate=[None]*4
		self.irsensor=[False]*4
		self.password=[0]*4
	def timerEvent(self,event):
		if event.timerId()==self.ardtimerid:
			if not self.ard.isOpen():
				qDebug('Try to connect to arduino...')
				portname=''
				for port in QSerialPortInfo.availablePorts():
					if 'Arduino Uno' in port.description():
						portname=port.portName()
				if portname!='':
					self.ard.setPort(QSerialPortInfo(portname))
					if self.ard.open(QIODevice.ReadWrite):
						self.ada.runnin=True
						self.ada.start()
						self.typingwidget.show()
						self.typingwidget.changeType(0)
						self.typingwidget.changeMode(False)
						self.typingwidget.clear()
						self.typingwidget.finishReading()
						# self.servotimerid=self.startTimer(10000,Qt.VeryCoarseTimer)
					else:
						qDebug('Failed to open '+portname+'!')
						qDebug('Error: '+self.ard.errorString())
				portname=self.defaultPort
				self.ard.setPort(QSerialPortInfo(portname))
				if self.ard.open(QIODevice.ReadWrite):
					self.ada.runnin=True
					self.ada.start()
					self.typingwidget.show()
					self.typingwidget.changeType(0)
					self.typingwidget.changeMode(False)
					self.typingwidget.clear()
					self.typingwidget.finishReading()
					# self.servotimerid=self.startTimer(10000,Qt.VeryCoarseTimer)
				else:
					qDebug('Failed to open '+portname+'!')
					qDebug('Error: '+self.ard.errorString())
		for i in range(4):
			if event.timerId()==self.servotimerid[i]:
				slot=i
				if self.parkingslotstate[slot]==None: # error
					pass
				elif self.parkingslotstate[slot]==True: # getting car
					if self.irsensor[slot]==False:
						self.typingwidget.updateParkingSlot(slot,False)
						
						self.parkingslotid[slot]=False
						self.password[slot]=0

						_id='irsensor'+str(i+1)
						self.ada.send_data(_id,'square-o')
				elif self.parkingslotstate[slot]==False: # parking car
					if self.irsensor[slot]==True:
						password=self.typingwidget.password
						self.parkingslotid[slot]=True
						self.password[slot]=password
						self.typingwidget.updateParkingSlot(slot,True)

						_id='irsensor'+str(i+1)
						self.ada.send_data(_id,'check-square-o')

				self.typingwidget.finishReading()

				self.parkingslotstate[slot]=None

				data=0b01000000 # tat servo
				data+=2**i # set i'th bit from 0 to 1
				self.ard.write(bytes(chr(data),'utf-8'))
				data=0b00000000 # tat den led
				self.ard.write(bytes(chr(data),'utf-8'))

				self.killTimer(self.servotimerid[i])
				self.servotimerid[i]=-1
				pass
	@pyqtSlot()
	def __receive_data_arduino(self):
		data=self.ard.readAll()
		# qDebug('size: '+str(len(data))+' ==========================================')
		for inf in data:
			d=sc.decode(ord(inf))
			# qDebug(format(ord(inf),'b'))
			if d['type']=='irsensor':
				data=0b00100000
				for i in range(4):
					# qDebug('irsensor'+str(i+1)+': '+str(d['irsensor'+str(i+1)]))
					_id='irsensor'+str(i+1)
					# newvalue=d[_id]
					# _id=i
					newvalue=(True if (d[_id]=='check-square-o') else False)
					# self.typingwidget.updateParkingSlot(i,(newvalue=='check-square-o'))
					# self.ada.send_data(_id,newvalue)
					self.irsensor[i]=newvalue
				
				pass
			elif d['type']=='flamesensor':
				if d['value']==1:
					self.ada.send_data('state','flame')
				else:
					self.ada.send_data('state','circle-o')
				pass
			elif d['type']=='keypad':
				key=d['key']
				# qDebug('keypad:'+key)
				if key in '0123456789*#': # action
					self.typingwidget.addKey(key)
				elif key=='n':
					qDebug('No key pressed!')
				else:
					qDebug('Error: Please choose a action')
			else:
				qDebug('Error: Unknowed signal (0b'+str(format(inf,'b'))+')')
			
	@pyqtSlot()
	def __receive_data_adafruit(self):
		for changed in self.ada.list_changed():
			if 'irsensor' in changed:
				pass
				# send data again to arduino
				# data=0b00000000
				# for i in range(4):
				# 	if self.ada.get_data('irsensor'+str(i+1))=='check-square-o':
				# 		data=setbit(data,i,1)
				# self.ard.write(bytes(chr(data),'utf-8'))
			elif 'door' in changed:
				state=self.ada.get_data('door')
				if state=='mocua':
					data=0b01010100
					self.ard.write(bytes(chr(data),'utf-8'))
				elif state=='dongcua':
					data=0b01000100
					self.ard.write(bytes(chr(data),'utf-8'))
				pass
	
	@pyqtSlot()
	def __getcar(self):
		park=self.typingwidget.park
		password=self.typingwidget.password
		if park!='':
			slot=int(park)-1
			qDebug(str(slot))
			if not (slot in [0,1,2,3]):
				self.typingwidget.notifical('Xin vui long nhap dung ma so de xe!')
			elif not self.parkingslotid[slot]:
				self.typingwidget.notifical('Cho trong nay hien chua co xe!')
			elif password!=self.password[slot]:
				self.typingwidget.notifical('Mat khau khong dung!')
			else:
				data=0b01010000
				servo=slot
				data=setbit(data,servo,1)
				self.ard.write(bytes(chr(data),'utf-8'))
				
				self.parkingslotstate[slot]=True
				self.servotimerid[servo]=self.startTimer(1000,Qt.VeryCoarseTimer)

				# bat den led
				data=0b00000000
				if park in '0102':
					data+=2**2+2**0
				elif park in '0304':
					data+=2**2+2**1
				self.ard.write(bytes(chr(data),'utf-8'))

				pass
		else:
			self.typingwidget.notifical('Xin vui long nhap dung ma so de xe!')
				
		# self.ard.write(bytes(chr(data),'utf-8'))
		self.typingwidget.finishReading()
	def __parkcar(self):
		park=self.typingwidget.park
		if park!='':
			slot=int(park)-1
			if not (slot in [0,1,2,3]):
				self.typingwidget.notifical('Xin vui long nhap dung ma so de xe!')
			elif self.parkingslotid[slot]:
				self.typingwidget.notifical('Noi do xe '+str(slot+1)+' da co nguoi, vui long chon noi do xe khac!')
			else:
				data=0b01010000
				# servo=int(slot/2)
				servo=slot
				qDebug(str(slot)+str(servo))
				data=setbit(data,servo,1)
				self.ard.write(bytes(chr(data),'utf-8'))
				
				# will be moved this block
				# self.parkingslotid[slot]=True
				self.parkingslotstate[slot]=False
				# self.password[slot]=password

				self.servotimerid[servo]=self.startTimer(1000,Qt.VeryCoarseTimer)

				# bat den led
				data=0b00000000
				if park in '0102':
					data+=2**2+2**0
				elif park in '0304':
					data+=2**2+2**1
				self.ard.write(bytes(chr(data),'utf-8'))

				qDebug('loo '+format(data,'b'))
				pass
		else:
			self.typingwidget.notifical('Xin vui long nhap dung ma so de xe!')
			
				
		
			
		
		

if __name__=='__main__':
	# print('Available port:')
	# for port in QSerialPortInfo.availablePorts():
	# 	print(port.portName(),'(',port.description(),')',sep='')
	# print('Select arduino port: ',end='')
	# app=Application(input().strip(),115200,sys.argv)
	portname='COM5'
	# for port in QSerialPortInfo.availablePorts():
	# 	if 'Arduino Uno' in port.description():
	# 		portname=port.portName()
	app=Application(portname,115200,sys.argv)
	# qDebug('??')
	
	
	app.exec()
	
