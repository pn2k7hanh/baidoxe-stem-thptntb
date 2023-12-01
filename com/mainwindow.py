from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui_mainwindow import Ui_MainWindow
from PyQt5.QtSerialPort import *

# from serialthread import Arduino

class MainWindow(QMainWindow):
	def __init__(self,parent=None):
		QMainWindow.__init__(self,parent)
		self.__define()


		self.ui.command.returnPressed.connect(self.__serialWrote)
		self.ui.actionConnect.triggered.connect(self.__connect)
		self.ui.actionDisconnect.triggered.connect(self.__disconnect)
		self.ard.readyRead.connect(self.__serialRead)
		self.ui.actionRefresh.triggered.connect(self.reloadPort)
		
		# self.reloadPort()

	def __define(self):
		self.ui=Ui_MainWindow()
		self.ui.setupUi(self)

		# default value
		self.port='COM5'
		self.baud=115200
		self.ard=QSerialPort()
		self.ard.setPort(QSerialPortInfo(self.port))
		self.ard.setBaudRate(self.baud)

		self.connected=False;
		
		#widget
		self.aport=list()
		self.lastPortChecked=self.ui.actionNoPort
		self.ui.actionNoPort.triggered.connect(self.changePort)
		
		self.size=0
	
	@pyqtSlot()
	def reloadPort(self):
		self.ui.actionNoPort.triggered.disconnect(self.changePort)
		for act in self.aport: # disconnect all signal-slot
			act.triggered.disconnect(self.changePort)
		
		self.ui.menuPort.clear()
		self.aport.clear()
		self.ui.menuPort.addAction(self.ui.actionRefresh)
		self.ui.menuPort.addSeparator()
		self.ui.menuPort.addAction(self.ui.actionNoPort)
		self.ui.actionNoPort.triggered.connect(self.changePort)
		
		for t in QSerialPortInfo.availablePorts():
			act=self.ui.menuPort.addAction("{} ({})".format(t.portName(),t.description()))
			act.setStatusTip(t.portName())
			act.triggered.connect(self.changePort)
			act.setCheckable(True)
			self.aport.append(act)
		
	@pyqtSlot()
	def changePort(self):
		act=self.sender()
		self.lastPortChecked.setChecked(False)
		act.setChecked(True)
		self.lastPortChecked=act
		if act.statusTip()!='noport':
			self.port=act.statusTip()
			self.ard.setPort(QSerialPortInfo(self.port))
	
	@pyqtSlot()
	def __serialWrote(self):
		if self.connected:
			text=self.ui.command.text()
			self.ard.write(bytes(text,'utf-8'))
		self.ui.command.clear()

	@pyqtSlot()
	def __serialRead(self):
		# qDebug(str(self.ard.bytesAvailable()))
		if self.size==0:
			if self.ard.bytesAvailable()>1:
				data=self.ard.read(1)
				self.size=data[0]
				# qDebug('Size: '+str(data)+'\nSizeofsize: '+str(len(data)))
				
		# qDebug(str(self.size))
		# qDebug(str(self.ard.bytesAvailable())+'\n\n\n')
		if self.ard.bytesAvailable()>=self.size:
			data=self.ard.read(self.size)
			string=''.join(map(chr,data))
			string=string[:-1]
			qDebug(str(data))
			if chr(3) in string:
				self.ard.readAll()
			else:
				self.ui.console.appendPlainText(string)
				# qDebug('Data: \"'+str(data)+'\"\nSizeofsize: '+str(len(data)))
				# qDebug(str(data))
				self.size=0
		
		# data=self.ard.readAll()
		# qDebug(str(data))
		# # self.ui.console.appendPlainText(''.join(map(chr,data)))
		# self.ui.console.appendPlainText(data.__str__())
				

	@pyqtSlot()
	def __connect(self):
		self.ard.open(QIODevice.ReadWrite)
		self.ui.actionConnect.setEnabled(False)
		self.ui.actionDisconnect.setEnabled(True)
		self.connected=True;
		

	@pyqtSlot()
	def __disconnect(self):
		self.ard.close()
		self.ui.actionConnect.setEnabled(True)
		self.ui.actionDisconnect.setEnabled(False)
		self.connected=False;






