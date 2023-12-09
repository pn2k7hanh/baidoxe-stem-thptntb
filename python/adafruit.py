from queue import Queue as queue
from collections import namedtuple

from PyQt5.QtCore import *
from Adafruit_IO import *

class Adafruit(QThread):
	data_changed=pyqtSignal()
	Transmit=namedtuple('Transmit',['type','feed','data'])
	Receive=namedtuple('Receive',['type','feed'])
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		self.__define()
	def __define(self):
		self.ada=Client('adantb','aio_CsHK50rpULPsgMeehqv4T7qRmtXy')
		self.data_mutex=QMutex()
		self.data=dict()
		self.data['irsensor1']='unknowed'
		self.data['irsensor2']='unknowed'
		self.data['irsensor3']='unknowed'
		self.data['irsensor4']='unknowed'
		self.data['state']='unknowed'
		self.data['door']='unknowed'
		self.runnin=True
		self.first_run=True
		self.queue_mutex=QMutex()
		self.queue=queue()
		self.list_change_mutex=QMutex()
		self.list_change=list()
		self.irsensor=['unknowed']*4
		self.irsensor_mutex=QMutex()
	def __add_to_queue():
		pass
	def send_data(self,feed,data):
		self.queue_mutex.lock()
		if 'irsensor' in feed:
			self.irsensor_mutex.lock()
			self.irsensor[int(feed[-1])-1]=data
			self.irsensor_mutex.unlock()
		else:
			self.queue.put(self.Transmit('Transmit',feed,data))
		self.queue_mutex.unlock()
	def get_data(self,feed=''):
		self.data_mutex.lock()
		data=self.data[feed]
		self.data_mutex.unlock()
		return str(data)
	def get_changed(self,feed):
		self.list_change_mutex.lock()
		value = (True if (feed in self.list_changed) else False)
		self.list_change_mutex.unlock()
		return value
	def list_changed(self):
		self.list_change_mutex.lock()
		changed=self.list_change
		self.list_change_mutex.unlock()
		return changed
	def run(self):
		qDebug("start thread")
		while self.runnin:
			qDebug('Fetching...')
			self.queue_mutex.lock() # put any thing you want to receive from adafruit io
			# if self.first_run:
			# 	self.queue.put(self.Receive('Receive','irsensor1'))
			# 	self.queue.put(self.Receive('Receive','irsensor2'))
			# 	self.queue.put(self.Receive('Receive','irsensor3'))
			# 	self.queue.put(self.Receive('Receive','irsensor4'))
			self.queue.put(self.Receive('Receive','door'))
			self.queue_mutex.unlock()
			# qDebug('debug')
			changed=False
			self.list_change_mutex.lock()
			self.list_change.clear()
			self.list_change_mutex.unlock()
			while not self.queue.empty():
				# QThread.msleep(500)
				action=self.queue.get()
				if action.type=='Transmit':
					self.data_mutex.lock()
					if self.data[action.feed]!=action.data:
						qDebug(action.feed+' loooooo '+action.data)
						self.ada.send_data(action.feed,action.data)
						self.data[action.feed]=action.data
					self.data_mutex.unlock()
				elif action.type=='Receive':
					data=self.ada.receive(action.feed)
					self.data_mutex.lock()
					if self.data[action.feed]!=data.value:
						qDebug(str(self.data[action.feed])+' h '+str(data.value))
						self.data[action.feed]=data.value
						changed=True
						self.list_change_mutex.lock()
						self.list_change.append(action.feed)
						self.list_change_mutex.unlock()
					self.data_mutex.unlock()

			# qDebug('debug')

			for i in range(4):
				# QThread.msleep(500)
				self.irsensor_mutex.lock()
				value=self.irsensor[i]
				self.irsensor_mutex.unlock()
				_id='irsensor'+str(i+1)
				self.data_mutex.lock()
				if self.data[_id]!=value:
					qDebug('Hehe: '+_id+' hmm '+value)
					self.ada.send_data(_id,value)
					self.data[_id]=value
				self.data_mutex.unlock()
			# qDebug('debug')

			if changed:
				self.data_changed.emit()
			
			
			if self.first_run:
				self.first_run=False
			QThread.sleep(1)
