import Adafruit_IO as Adafruit
from Adafruit_IO import MQTTClient
import time

from PyQt5.QtWidgets import QApplication
import sys

from mainwindow import MainWindow

# ada = Adafruit.Client('adantb','aio_ZoHe640lcxVlcFCGOFYAHxN01bVj')

aio = MQTTClient('adantb','aio_ZoHe640lcxVlcFCGOFYAHxN01bVj')

if __name__ == '__main__':
	app=QApplication(sys.argv)

	w=MainWindow()
	w.show()

	app.exec()
	
	
	
	# aio.loop()
	
	# print(ada.feeds())
	
	pass
