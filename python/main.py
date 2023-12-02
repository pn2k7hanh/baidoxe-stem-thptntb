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
		
		self.parkingslot=[1]*4
		for i in range(4):
			self.typingwidget.updateParkingSlot(i,self.parkingslot[i])
		
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
		self.username=[]
		self.password=[]
		self.servotimerid=-1
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
						self.servotimerid=self.startTimer(10000,Qt.VeryCoarseTimer)
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
					self.servotimerid=self.startTimer(10000,Qt.VeryCoarseTimer)
				else:
					qDebug('Failed to open '+portname+'!')
					qDebug('Error: '+self.ard.errorString())
		# elif event.timerId()==self.servotimerid:
		# 	data=0b00100001
		# 	self.ard.write(bytes(chr(data),'utf-8'))
		# 	qDebug('hmm')
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
					newvalue=d[_id]
					# qDebug(_id+' ir '+newvalue)
					self.typingwidget.updateParkingSlot(i,(newvalue=='check-square-o'))
					# qDebug(self.ada.get_data(_id)+' lo '+newvalue)
					# if self.ada.get_data(_id)!=newvalue:
					self.ada.send_data(_id,newvalue)
					tmp_i = (0 if (i in [0,1]) else 1)
					if newvalue=='check-square-o':
						data=setbit(data,tmp_i,1)
				self.ard.write(bytes(chr(data),'utf-8'))
				
				pass
			elif d['type']=='flamesensor':
				# qDebug('flamesensor: '+str(d['value']))
				# if self.ada.get_data('flamesensor'):
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
	
	@pyqtSlot()
	def __getcar(self):
		park=self.typingwidget.park
		# show the led
		data=0b00000000
		if park!='':
			if park in '0102':
				if False:
					pass
				else:
					data+=2**2+2**0
			elif park in '0304':
				if False:
					pass
				else:
					data+=2**2+2**1
			else:
				self.typingwidget.notifical('Xin vui long nhap dung ma so de xe!')
				
		self.ard.write(bytes(chr(data),'utf-8'))
		self.typingwidget.finishReading()
	def __parkcar(self):
		park=self.typingwidget.park
		# show the led
		data=0b00000000
		if park!='':
			if park in '0102':
				if False:
					pass
				else:
					data+=2**2+2**0
			elif park in '0304':
				if False:
					pass
				else:
					data+=2**2+2**1
		self.typingwidget.finishReading()
			
		
		

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
	
