from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui_typingwidget import Ui_TypingWidget

# import rc_typingwidget

class MessageBox(QMessageBox):
	ok=pyqtSignal()
	cancel=pyqtSignal()
	def __init__(self,parent=None):
		QMessageBox.__init__(self,parent)
		self.timeoutid=0
	def notic(self,text,info):
		self.setIcon(QMessageBox.Critical)
		# self.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
		self.setText(text)
		self.setInformativeText(info)
		self.setWindowTitle('Thong bao')
		self.show()
		self.timeoutid=self.startTimer(5000)
		self.buttonClicked.connect(self.__buttonClicked)
	@pyqtSlot(QAbstractButton)
	def __buttonClicked(self,button):
		text=button.text()
		if 'Ok' in text:
			self.ok.emit()
		elif 'Cancel' in text:
			self.cancel.emit()
		else:
			qDebug('Another button was pressed!')
	def timerEvent(self,event):
		self.killTimer(event.timerId())
		if event.timerId() == self.timeoutid:
			self.hide()
			self.ok.emit()

class TypingWidget(QWidget):
	getcar=pyqtSignal()
	parkcar=pyqtSignal()
	def __init__(self,parent=None):
		QWidget.__init__(self,parent)
		self.ui=Ui_TypingWidget()
		self.ui.setupUi(self)
		self.type=0
		self.changed=False
		# self.list_type=['IDUSER','PASSWORD','SLOTPARK']
		self.finishReading()
		self.t=[QLabel(str(i+1),[self.ui.slWidget,
								self.ui.pwWidget,
								self.ui.cancleButton,
								self.ui.getcarButton,
								self.ui.parkcarButton][i]) for i in range(5)]
		self.irsensor=[self.ui.irsensor1,
					self.ui.irsensor2,
					self.ui.irsensor3,
					self.ui.irsensor4]
		redPalette=QPalette()
		redPalette.setBrush(QPalette.Text,QBrush(Qt.red))
		redPalette.setBrush(QPalette.WindowText,QBrush(Qt.red))
		for label in self.t:
			label.setPalette(redPalette)
			font=label.font()
			font.setPointSize(16)
			label.setFont(font)
		self.changeMode(False)
		self.messagebox=MessageBox()
		self.messagebox.ok.connect(self.__ok)
		self.messagebox.cancel.connect(self.__cancel)
	def showEvent(self,event):
		for label in self.t:
			parent=label.parentWidget()
			label.setGeometry(parent.width()-16,0,16,21)
	def resizeEvent(self,event):
		for label in self.t:
			parent=label.parentWidget()
			label.setGeometry(parent.width()-16,0,16,21)
	def finishReading(self):
		# self.iduser=''
		self.password=''
		self.park=''
	def changeMode(self,checked=False):
		if checked:
			self.ui.helpLabel.show()
			for label in self.t:
				label.show()
		else:
			self.ui.helpLabel.hide()
			for label in self.t:
				label.hide()
	def changeType(self,tp):
		if self.type==tp:
			return
		
		# if tp==0:
		# 	self.ui.idWidget.setEnabled(True)
		if tp==0:
			self.ui.slWidget.setEnabled(True)
		elif tp==1:
			self.ui.pwWidget.setEnabled(True)
		
		# if self.type==0:
		# 	self.ui.idWidget.setEnabled(False)
		if self.type==0:
			self.ui.slWidget.setEnabled(False)
		elif self.type==1:
			self.ui.pwWidget.setEnabled(False)
		
		self.type=tp
	def keyPressEvent(self,event):
		if event.key() in [Qt.Key_0,Qt.Key_1,Qt.Key_2,Qt.Key_3,Qt.Key_4,Qt.Key_5,Qt.Key_6,Qt.Key_7,Qt.Key_8,Qt.Key_9]:
			key=event.key()-Qt.Key_0
			self.addKey(str(key))
		elif event.key() in [Qt.Key_Return,Qt.Key_Enter]:
			self.addKey('#')
		pass
	def updateParkingSlot(self,n,state=True):
		if state:
			self.irsensor[n].setPixmap(QPixmap(':/check-square-o'))
		else:
			self.irsensor[n].setPixmap(QPixmap(':/square-o'))
	def addKey(self,key):
		if key=='#':
			self.changed=(not self.changed)
			self.changeMode(self.changed)
		elif key in '0123456789':
			if self.changed:
				self.changed=(not self.changed)
				self.changeMode(self.changed)
				if key in '12':
					self.changeType(int(key)-1)
				elif key in '345':
					if key=='4':
						# self.iduser=self.ui.idBox.text()
						self.password=self.ui.pwBox.text()
						self.park=self.ui.slBox.text()
						self.getcar.emit()
					elif key=='5':
						# self.iduser=self.ui.idBox.text()
						self.password=self.ui.pwBox.text()
						self.park=self.ui.slBox.text()
						self.parkcar.emit()
					# elif key=='3':
					self.clear()
			# elif self.type==0:
			# 	text=self.ui.idBox.text()
			# 	text+=key
			# 	self.ui.idBox.setText(text)
			elif self.type==0:
				text=self.ui.slBox.text()
				text+=key
				self.ui.slBox.setText(text)
			elif self.type==1:
				text=self.ui.pwBox.text()
				text+=key
				self.ui.pwBox.setText(text)
	def clear(self):
		# self.ui.idBox.setText('')
		self.ui.slBox.setText('')
		self.ui.pwBox.setText('')
		self.changeType(0)
	def notifical(self,s):
		self.messagebox.notic('Loi',s)
	@pyqtSlot()
	def __ok(self):
		qDebug('Ok, clear input!')
		self.clear()
	@pyqtSlot()
	def __cancel(self):
		qDebug('Cancel!')