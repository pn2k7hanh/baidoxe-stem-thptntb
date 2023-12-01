from Adafruit_IO import Client, Feed

from PyQt5.QtCore import *

class Adafruit(QThread):
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		